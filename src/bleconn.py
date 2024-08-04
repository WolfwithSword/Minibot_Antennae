from utils import Utils, _USE_WIFI
from pinmgr import PinManager
from micropython import const

from utils import Utils, _USE_WIFI, _USE_BLE, _USE_NONE

try:
    import uasyncio as asyncio
except:
    import asyncio

import aioble, bluetooth

class BLEConn():
    
    def __init__(self, pins: PinManager, _utils: Utils):
        self.utils = _utils
        self.uuid = _utils.config.get('ble', {}).get('uuid', '6094935a-ba8d-4fbb-9150-904e3244610b')
        self.pins = pins
        self.name = _utils.config.get('ble', {}).get('name', 'minibot_AT')
        self.poll_time = _utils.config.get('ble', {}).get('poll_time', 5)
        
    async def start_ble(self):
        _BLE_SERVICE_UUID = bluetooth.UUID(self.uuid)
        _BLE_SENSOR_BAT = bluetooth.UUID(0x2BF0)
        _BLE_SENSOR_UPT = bluetooth.UUID(0x183F)
        
        _BLE_CTRL_MODE = bluetooth.UUID(0x04C3)
        
        
        _BLE_CTRL_DELAY = bluetooth.UUID(0x77DB) # set LED delay in milliseconds
        # (NOT SECONDS which is in config)
        # will be divided
        # Only pass in UINT16 BIG ENDIAN

        _BLE_CTRL_STEPS = bluetooth.UUID(0x77DC) #UINT8
        
        _BLE_CTRL_LED = bluetooth.UUID(0x77DA) # left on or off (on on on is restart)
        # 0 = Left Off
        # 1 = Left On
        # 2 = Right Off
        # 3 = Right On
        # 4 = Sync On
        # 5 = Sync Off
                                       
        # Advertising beacons Frequency
        _ADV_INTERVAL_MS = 250_000
        ble_service = aioble.Service(_BLE_SERVICE_UUID)
        
        led_characteristic = aioble.Characteristic(ble_service, _BLE_CTRL_LED, read=True, write=True, notify=True, capture=True)
        mode_characteristic = aioble.Characteristic(ble_service, _BLE_CTRL_MODE, read=True, write=True, notify=True, capture=True)
        delay_characteristic = aioble.Characteristic(ble_service, _BLE_CTRL_DELAY, read=True, write=True, notify=True, capture=True)
        steps_characteristic = aioble.Characteristic(ble_service, _BLE_CTRL_STEPS, read=True, write=True, notify=True, capture=True)
        
        battery_sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_BAT, read=True, notify=True)
        uptime_sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_UPT, read=True, notify=True)
        

        aioble.register_services(ble_service)
        
        def _encode_data(data):
            return str(data).encode('utf-8')
        def _decode_data(data):
            try:
                if data is not None:
                    # Decode the UTF-8 data
                    number = int.from_bytes(data, 'big')
                    return number
            except Exception as e:
                print("Error decoding value:", e)
                return None
            
        async def sensor_tasks():
            while True:
                battery_sensor_characteristic.write(_encode_data(self.pins.get_battery_voltage()), send_update=True)
                uptime_sensor_characteristic.write(_encode_data(self.utils.get_elapsed_time()), send_update=True)
                await asyncio.sleep(self.poll_time)
        
        async def peripheral_task():
            while True:
                try:
                    async with await aioble.advertise(
                        _ADV_INTERVAL_MS,
                        name=self.name,
                        services=[_BLE_SERVICE_UUID],
                        ) as connection:
                            print("Connection from", connection.device)
                            await connection.disconnected()             
                except asyncio.CancelledError:
                    # Catch the CancelledError
                    print("Peripheral task cancelled")
                except Exception as e:
                    print("Error in peripheral_task:", e)
                finally:
                    # Ensure the loop continues to the next iteration
                    await asyncio.sleep_ms(100)
        
        async def wait_for_mode_write():
            while True:
                try:
                    connection, data = await mode_characteristic.written()
                    data = _decode_data(data)
                    print('Connection: ', connection)
                    print('Data: ', data)
                    if data == _USE_WIFI:
                        self.utils.switch_mode(_USE_WIFI)
                    else:
                        print('Unknown command')
                except asyncio.CancelledError:
                    # Catch the CancelledError
                    print("Peripheral task cancelled")
                except Exception as e:
                    print("Error in peripheral_task:", e)
                finally:
                    # Ensure the loop continues to the next iteration
                    await asyncio.sleep_ms(100)
                    
        async def wait_for_led_write():
            while True:
                try:
                    connection, data = await led_characteristic.written()
                    data = _decode_data(data)
                    print('Connection: ', connection)
                    print('Data: ', data)
                    if data == 0:
                        self.pins.stop_left_light()
                    elif data == 1:
                        self.pins.start_left_light()
                    elif data == 2:
                        self.pins.stop_right_light()
                    elif data == 3:
                        self.pins.start_right_light()
                    elif data == 4:
                        self.pins.stop_sync_lights()
                    elif data == 5:
                        self.pins.start_sync_lights()
                    else:
                        print('Unknown command')
                except asyncio.CancelledError:
                    # Catch the CancelledError
                    print("Peripheral task cancelled")
                except Exception as e:
                    print("Error in peripheral_task:", e)
                finally:
                    # Ensure the loop continues to the next iteration
                    await asyncio.sleep_ms(100)

            
        async def wait_for_delayms_write():
            # UINT16 Big Endian only
            while True:
                try:
                    connection, data = await delay_characteristic.written()
                    data = _decode_data(data)
                    print('Connection: ', connection)
                    print('Data: ', data)
                    delay = -1
                    if data is not None:
                        if isinstance(data, int):
                            if data == 0:
                                delay = 0
                            else:
                                delay = float(data / 1000.0)
                        elif isinstance(data, float):
                            delay = float(data / 1000.0)
                            if data > 0 and data < 1:
                                delay = data
                        elif isinstance(data, str):
                            try:
                                delay = float(data)
                            except:
                                delay = -1
                        if delay >= 0:
                            if delay == 0: # Default
                                delay = 0.03
                            self.pins.set_delay(delay)
                        else:
                            print('Unknown command')
                except asyncio.CancelledError:
                    # Catch the CancelledError
                    print("Peripheral task cancelled")
                except Exception as e:
                    print("Error in peripheral_task:", e)
                finally:
                    # Ensure the loop continues to the next iteration
                    await asyncio.sleep_ms(100)

            
        async def wait_for_steps_write():
            # UINT8
            while True:
                try:
                    connection, data = await steps_characteristic.written()
                    data = _decode_data(data)
                    print('Connection: ', connection)
                    print('Data: ', data)
                    steps = data
                    if data is not None:
                        if steps == 0:
                            steps = 32
                        if steps >= 0:
                            self.pins.set_steps(steps)
                        else:
                            print('Unknown command')
                except asyncio.CancelledError:
                    # Catch the CancelledError
                    print("Peripheral task cancelled")
                except Exception as e:
                    print("Error in peripheral_task:", e)
                finally:
                    # Ensure the loop continues to the next iteration
                    await asyncio.sleep_ms(100)

        async def run():
            print("Running BLE")
            t1 = asyncio.create_task(sensor_tasks())
            t2 = asyncio.create_task(peripheral_task())
            t3 = asyncio.create_task(wait_for_mode_write())
            t4 = asyncio.create_task(wait_for_led_write())
            t5 = asyncio.create_task(wait_for_delayms_write())
            t6 = asyncio.create_task(wait_for_steps_write())
            await asyncio.gather(t1, t2, t3, t4, t5, t6)
        
        await run()
    
    async def run(self):
        await self.start_ble()

