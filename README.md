# Minibot_Antennae
Micropython-ESP32 code for custom antennae control based on Ellie Minibot's OC's antennae. WiFi and BLE servers included for control.

Three green LEDs will be controlled by monitoring a connected LiPo battery voltage (not capacity!)

Two LEDs (one on each side) on the antennae bulbs will be PWM controlled in a fading sequence. These can be synced or toggled on/off individually via various control endpoints and services. By default on boot, they will be synced ON.

By default, WiFi Mode is enabled.

# Setup

## MicroPython

- Download [esptool](https://github.com/espressif/esptool)
- Flash your board
  - Replace below command with the appropriate COM# port you plugged in to for the board 
  - `./esptool.exe --port COM# erase_flash`

- Flash with MicroPython
  - Download latest for [ESP32](https://micropython.org/download/ESP32_GENERIC/)
  - Replace COM# with yours below, as well as correct MicroPython binary downloaded
  - `./esptool.exe --chip esp32 --port COM# --baud 460800 write_flash -z 0x1000 .\ESP32_GENERIC-20240602-v1.23.0.bin`

## IDE

I recommend using [Thonny](https://github.com/thonny/thonny)

You can easily download the dependencies to the board through it.

## Dependencies

- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble)
  - Make sure it's the micropython lib
  
## Install

Simply save each of the files in `/src/*` to the root of the board (do not include the src folder itself). Preserve all filenames

Modify `config.json` as required. These will be the default settings on every boot.

Note: This file may be written to, but it will only ever chande "mode"

## Materials

See `parts` for details

// TODO - BOM, Circuit diagram, STLs

# Usage

## Configuration

```json
{
    "wifi": {
        "name": "minibot_AT", // Access point SSID
        "ap_password": "eBot4do8", // Access point Password. Please Change
        "max_connections": 2, // Max number of listeners allowed for the socket control server
        "port": 8080 // Port for accessing the socket control server
    },
    "ble": {
        "name": "minibot_AT", // Bluetooth device name
        "uuid": "6094935a-ba8d-4fbb-9150-904e3244610b", // BLE Service Advertised UUID
        "poll_time": 5 // How often to update BLE read-only sensors
    },
    "mode": 1, // Which mode to boot in.
    "pwm": {  // PWM pins are the Antennae bulbs only.
        "frequency": 500, // Frequency of PWM pins. 
        "delay": 0.03, // Delay between fading steps. Min 0.01.
        "off_time": 0.05, // Time to remain fully off during fades
        "on_time": 0.5, // Time to remain fully on during fades
        "step": 32 // Step count from 0-1024 and 1024-0 for LED brightness in between delays. Min 8
    },
    "leds": { // If true, the LED can be active.
        "green1": true, 
        "green2": true,
        "green3": true,
        "left": true,
        "right": true,
        "sync_sides": true
    },
    "poll_time": 2 // Poll time to check for battery voltage in main loop.
}
```

Mode values:
  - 0: None
    - No WiFi Socket or BLE Server active. Can only set with direct access to the board and changing the config on-board.
  - 1: WiFi
    - Enables WiFi. Will create an AP to connect to and configure a 2.4Ghz WiFi to connect to and save details for.
    - When successfully connected to a WiFi, will create a socket server at the specified port
  - 2: BLE
    - Enables the BLE server


## WiFi

### Endpoints
  - GET
    - /, /data
      - Returns JSON with **battery_voltage** and **uptime_s** 
        - Example`{"battery_voltage": 4.135, "uptime_s": 155.984}`
    - /restart
      - Hard-restart the board
    - /mode/1
      - Tells you that you're dumb cause you're already in WiFi Mode
    - /mode/2
      - Switch to BLE and restart board
    - /leds/right/off
      - Turn OFF Right Antenna LED
    - /leds/right/on
      - Turn ON Right Antenna LED
    - /leds/left/off
      - Turn OFF Left Antenna LED
    - /leds/left/on
      - Turn ON Left Antenna LED
    - /leds/sync/off
      - Turn OFF Antenna LEDs (Sync)
    - /leds/sync/on
      - Turn ON Antenna LEDs (Sync)
    - All other endpoints result in HTTP 404. All previous in HTTP 200

## BLE

### Services & Characteristics
  
  - Battery Voltage: **0x2BF0**
  - Uptime Sensor (Seconds): **0x183F**
  - Switch Modes: **0x04C3**
    - 1 *uint*: Switch to WiFi and restart board
    - All other inputs ignored
  - LED Control: **0x77DA**
    - 0 *uint* - Turn OFF Left Antenna LED
    - 1 *uint* - Turn ON Left Antenna LED
    - 2 *uint* - Turn OFF Right Antenna LED
    - 3 *uint* - Turn ON Right Antenna LED
    - 4 *uint* - Turn OFF Antenna LEDs (Sync)
    - 5 *uint* - Turn ON Antenna LEDs (Sync)
    - All other inputs ignored
    