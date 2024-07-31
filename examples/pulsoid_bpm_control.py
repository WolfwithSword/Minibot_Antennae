import requests
import time
import websocket
import json

# pip install websocket-client
# pip install requests

global current_setting
current_setting = 0

settings = [
    "?delay=default&steps=default",
    "?delay=0.02&steps=default",
    "?delay=0.02&steps=64",
    "?delay=0.012&steps=64",
    "?delay=0,012&steps=128"
    ]

# Either use Pulsoid bro plan for websocket API, or go to your free browser source URL, open inspect element network tab and look for the websocket URL for that browser source.
# &response_mode=legacy_json is optional. This is built to work with both. It also works with response_type=plaintext
pulsoid_ws_url = "wss://dev.pulsoid.net/api/v1/data/real_time?access_token=YOUR_TOKEN_HERE&response_mode=legacy_json"

at_host = "minibot_AT.local"
at_port = 8080

at_url = f"http://{at_host}:{at_port}"
path = "/leds"

# Init
# Sync the LEDs, which will also restart them
r = requests.get(f"{at_url}{path}/sync/on")

# Set initial to the default params
r = requests.get(f"{at_url}{path}{settings[current_setting]}")

# Note: there is no error handling if the antenna are unreachable. Run this script only when they are :) 

def on_open(ws):
    print("Connected to WS")
    
def on_close(ws):
    print("WS Closed")
    
def on_error(ws, error):
    print("Error: ", error)
    
def on_message(ws, msg):
    global current_setting
    new_setting = current_setting
    if not msg:
        return
    if "response_mode=text_plain_only_heart_rate" in pulsoid_ws_url:
        result = int(msg)
    else:
        data = json.loads(msg).get('data', {})
        result = data.get('heartRate', data.get('heart_rate', -1))
    if result == -1:
        print(f"Error, did not find heartrate in response")
        print(msg)
        return

    # Adjust ranges here as needed
    if result <= 75:
         new_setting = 0
    elif 75 < result <= 90:
        new_setting = 1
    elif 90 < result <= 100:
        new_setting = 2
    elif 100 <= result < 120:
        new_setting = 3
    elif result >= 120:
        new_setting = 4

    if new_setting != current_setting:
        current_setting = new_setting
        s = f"{at_url}{path}{settings[current_setting]}"
        #print(s)
        #print(result)
        r = requests.get(s)


ws = websocket.WebSocketApp(
        pulsoid_ws_url,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
        header={}
    )

ws.run_forever()
