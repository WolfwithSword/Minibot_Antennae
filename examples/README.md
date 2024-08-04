# Example Integrations

## Pulsoid BPM Control

`pulsoid_bpm_control.py` can be run on a desktop with python (required dependencies: `websocket-client` and `requests`)

Configuration required for a websocket that provides heartrate in terms of whole numbers, such as from Pulsoid. Comments in the code describe how you can get the websocket URL if you do not know.

Additional config may be needed for the hostname and port of the Antennae instance in **WiFi Mode**.

This script will listen for the BPM reported by the websocket connection and depending on the ranges it is in, will adjust the PWM Fade/Pulse rate of the antennae tips.

Unless modified, default settings are: 

Delay is in seconds

- BPM <= 75: Default delay (0.03), Default steps (32)
- BPM 75-90: Delay 0.02, Default steps (32)
- BPM 90-100: Delay 0.02, Steps 64
- BPM 100-120: Delay 0.12, Steps 64
- BPM 120+: Delay 0.12, Steps 128