from pinmgr import PinManager
from utils import Utils, _USE_BLE
from micropython import const
import ure
import errno

try:
    import utime as time
except:
    import time
    
try:
    import usocket as socket
except:
    import socket
    
import wifimgr

_HTTP_OK = const('HTTP/1.1 200 OK\n')
_URL_RE = const("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP")
_METHOD_RE = const("^(GET|POST|PATCH|DELETE) /")
_PLAIN_TXT = const('Content-Type: text/plain\n')

def get_url(request):
    if "HTTP" not in request:
        return '', ''
    
    try:
        url = ure.search(_URL_RE, request).group(1).decode("utf-8").rstrip("/")
        method = ure.search(_METHOD_RE, request).group(1).decode("utf-8")
    except Exception:
        url = ure.search(_URL_RE, request).group(1).rstrip("/")
        method = ure.search(_METHOD_RE, request).group(1)
    url = "/" + url
    return url.strip(), method.strip()

_data = {}

class WiFiConn():
    
    def __init__(self, pins: PinManager, _utils: Utils):
        self.pins = pins
        self.utils = _utils

    def req_handler(self, cs):
        try:
            req = cs.read()
            if req:
                url, method = get_url(req)
                
                if method == 'GET':
                    if url in ['/', '/data']:
                        _data['battery_voltage'] = self.pins.get_battery_voltage()
                        _data['uptime_s'] = self.utils.get_elapsed_time()
                        rep = _data
                        cs.send(_HTTP_OK)
                        cs.send('Content-Type: application/json\n')
                    elif url.startswith('/restart'):
                        cs.send(_HTTP_OK)
                        cs.send(_PLAIN_TXT)
                        rep = 'Restarting...'
                        cs.send('Connection: close\n\n')
                        cs.sendall(rep)
                        time.sleep(1)
                        cs.close()
                        self.utils.restart()
                        return
                    elif url.startswith('/leds/'):
                        if url == '/leds/right/off':
                            pins.stop_right_light()
                        elif url == '/leds/right/on':
                            pins.start_right_light()
                        elif url == '/leds/left/off':
                            pins.stop_left_light()
                        elif url == '/leds/left/on':
                            pins.start_left_light()
                        elif url == '/leds/sync/off':
                            pins.stop_sync_lights()
                        elif url == '/leds/sync/on':
                            pins.start_sync_lights()
                        cs.send(_HTTP_OK)
                        cs.send(_PLAIN_TXT)
                        rep = 'OK'
                    elif url.startswith('/mode/set/'):
                        cs.send(_HTTP_OK)
                        cs.send(_PLAIN_TXT)
                        
                        # Mode 0 will be irrecoverable without reflashing
                        if url == '/mode/1':
                            # Already in Mode 1 because this is wifi
                            rep = 'Already in WiFi Mode'
                        elif url == '/mode/2':
                            rep = 'Switching to BLE...'
                            cs.send('Connection: close\n\n')
                            cs.sendall(rep)
                            time.sleep(2)
                            cs.close()
                            self.utils.switch_mode(_USE_BLE)
                            return
                    else:
                        rep = 'Not Found'
                        cs.send('HTTP/1.1 404 NOT FOUND\n')
                        cs.send(_PLAIN_TXT)
                else:
                    rep = 'Not Found'
                    cs.send('HTTP/1.1 404 NOT FOUND\n')
                    cs.send(_PLAIN_TXT)
            
                cs.send('Connection: close\n\n')
                cs.sendall(str(rep).replace("'", '"'))
                #print(rep)
            else:
                print('Client close connection')
        except Exception as e:
            print('Err:', e)
        cs.close()

    def cln_handler(self, srv):
        cs = None
        try:
            cs,ca = srv.accept()
            cs.setblocking(False)
            #cs.settimeout(5)
            cs.setsockopt(socket.SOL_SOCKET, 20, self.req_handler)
        except Exception as e:
            print("Exception in cln_handler: ", e)
            if cs:
                cs.close()
                
        
    def start_socket(self, ignore_error=False):
        try: 
            port = self.utils.config.get('wifi', {}).get('port', 8080)
            addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(addr)
            sock.listen(self.utils.config.get('wifi', {}).get('max_connections', 2)) # Max number of clients
            #srv.settimeout(5)
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, 20, self.cln_handler)
            return sock
        except OSError as e:
            if not ignore_error:
                print("Restarting due to socket error: ", e)
                self.utils.restart()
                
    def start(self):
        wlan = wifimgr.get_connection()
        if wlan is None:
            print("Unable to initialize network connection")
            while True:
                pass
        print("IP is: "+wlan.ifconfig()[0])
        #wlan_sta.config(dhcp_hostname=config['wifi']['device_hostname'])
        _sock = self.start_socket()
        return _sock
    
    
    def run(self):
        print("Running WiFi")
        _sock = self.start()
        while True:
            time.sleep(10)
            if _sock:
                try:
                    # Test socket is still up
                    _sock.sendall("test")
                except OSError as oe:
                    if oe.args[0] != errno.EAGAIN:
                        _sock = None
                        gc.collect()
                        print("Restarting Socket...")
                        _sock = self.start_socket(ignore_error=True)
                except Exception as e1:
                    try:
                        _sock.close()
                    except Exception as e2:
                        pass
                    _sock = None
                    gc.collect()
                    print("Restarting Socket...")
                    _sock = self.start_socket(ignore_error=True)
            pass
