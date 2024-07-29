from machine import reset as machine_reset
try:
    import utime as time
except:
    import time
try:
    import ujson as json
except:
    import json
    
# Cant const as importing in others
_USE_NONE = 0
_USE_WIFI = 1
_USE_BLE = 2

_CONFIG_FILE = const('config.json')

class Utils():
    
    def __init__(self):
        self._start_ticks = time.ticks_ms()
        self.get_config()

    def get_elapsed_time(self):
        return time.ticks_diff(time.ticks_ms(), self._start_ticks) / 1000
    
    def restart(self):
        machine_reset()
        
    def get_config(self):
        self.config = {}
        with open(_CONFIG_FILE) as f:
            self.config = json.load(f)

    def switch_mode(self, m: int):
        if m not in [_USE_NONE, _USE_WIFI, _USE_BLE]:
            return
        self.get_config()
        self.config['mode'] = m
        with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f)
        self.restart()
