from micropython import const

try:
    import utime as time
except:
    import time

import _thread as th

from pinmgr import PinManager
from utils import Utils, _USE_WIFI, _USE_BLE, _USE_NONE
from wificonn import WiFiConn
from bleconn import BLEConn

try:
    import uasyncio as asyncio
except:
    import asyncio

import aioble, bluetooth


import gc
gc.collect()
#print(gc.mem_free())

_utils = Utils()

print(_utils.config)

#############
MODE = _utils.config.get('mode', _USE_WIFI)
#############

print("Starting...")

# g1 = Bottom Green
# g2 = Middle Green
# g3 = Top Green
# left = Left Antennae bulb
# right = Right Antennae bulb
# bat_pin = Internal Battery Voltage ADC
pins = PinManager(g1=17, g2=16, g3=4, left=26, right=12, bat_pin=34, pwm_pins=[26,12], _utils=_utils)


_data = {
    "battery_voltage": 0.0,
}

time.sleep(1)

POLL_TIME = _utils.config.get('poll_time')
def main_monitor():
    while True:
        pins.green_led_battery_controller()
        time.sleep(POLL_TIME)
        #print(gc.mem_free())
        if (gc.mem_free() < 32000):
            gc.collect()
        if (gc.mem_free() < 7500):
            print("RESTARTING. LOW MEMORY")
            _utils.restart()
            
####################

th.start_new_thread(main_monitor, [])
time.sleep(1)
pins.start_sync_lights()
    
if MODE == _USE_WIFI:
    wifi_conn = WiFiConn(pins=pins, _utils=_utils)
    th.start_new_thread(wifi_conn.run, [])
elif MODE == _USE_BLE:
    ble_conn = BLEConn(pins=pins, _utils=_utils)
    asyncio.run(ble_conn.run())


