from machine import Pin, ADC, PWM
import _thread as th
from utils import Utils
try:
    import utime as time
except:
    import time
import gc

class PinManager():
    
    def __init__(self, g1: int, g2: int, g3: int, left: int, right: int, bat_pin: int,
                 pwm_pins: list, _utils: Utils):
        
        self._config = _utils.config
        
        self.battery_pin = ADC(bat_pin)
        self.battery_pin.atten(ADC.ATTN_11DB)
        
        self.green_1 = Pin(g1, Pin.OUT)
        self.green_2 = Pin(g2, Pin.OUT)
        self.green_3 = Pin(g3, Pin.OUT)
        
        self.left_led = Pin(left, Pin.OUT)
        self.right_led = Pin(right, Pin.OUT)

        self.left_led_pwm = None
        self.right_led_pwm = None
        
        self.set_delay(self._config.get("pwm", {}).get('delay', 0.01))
        self.set_steps(self._config.get("pwm", {}).get('step', 8))
        self.on_time_mult = self._config.get("pwm", {}).get('on_time_multiplier', 4.0)
        self.off_time_mult = self._config.get("pwm", {}).get('off_time_multiplier', 1.2)
        
        self.leds = self._config.get('leds', {})
        # Direct var references fix most of the mem leak un _run methods
        self.right_led_enabled = self.leds['right']
        self.left_led_enabled = self.leds['left']
        self.sync_leds_enabled = self.leds['sync_sides']
        self.g1_enabled = self.leds['green1']
        self.g2_enabled = self.leds['green2']
        self.g3_enabled = self.leds['green3']
        
        for p in pwm_pins:
            if p == left:
                self.left_led_pwm = PWM(self.left_led)
            elif p == right:
                self.right_led_pwm = PWM(self.right_led)
                
        pwm_freq = self._config.get("pwm", {}).get("frequency", 5000)
        
        if self.left_led_pwm:
            self.left_led_pwm.init(freq=pwm_freq, duty=0)
        if self.right_led_pwm:
            self.right_led_pwm.init(freq=pwm_freq, duty=0)
        
        self.pwm_pin_d = {
            "left_pwm": self.left_led_pwm,
            "right_pwm": self.right_led_pwm
        }
        
        self.init_off()
        
    def init_off(self):
        states = {
            "g1": 0,
            "g2": 0,
            "g3": 0,
            "left": 0,
            "right": 0,
            "left_pwm": 0,
            "right_pwm": 0
        }

        self.set_pins(states)
        states = None
        del states
        
    def set_pins(self, status:dict):
        if not self.leds:
            return
        if status.get('g1') is not None and (self.g1_enabled or status.get('g1') == 0):
            self.green_1.value(status.get('g1'))
        if status.get('g2') is not None and (self.g2_enabled or status.get('g2') == 0):
            self.green_2.value(status.get('g2'))
        if status.get('g3') is not None and (self.g3_enabled or status.get('g3') == 0):
            self.green_3.value(status.get('g3'))
        if status.get('left') is not None and (self.left_led_enabled or status.get('left') == 0):
            self.left_led.value(status.get('left'))
        if status.get('right') is not None and (self.right_led_enabled  or status.get('right') == 0):
            self.right_led.value(status.get('right'))
        
        if status.get('left_pwm') is not None:
            if self.left_led_pwm and (self.left_led_enabled or status.get('left_pwm') == 0):
                self.left_led_pwm.duty(status.get('left_pwm'))
        if status.get('right_pwm') is not None:
            if self.right_led_pwm and (self.right_led_enabled or status.get('right_pwm') == 0):
                self.right_led_pwm.duty(status.get('right_pwm'))
        status = None
        del status
        
        
    def get_battery_voltage(self):
        if self.battery_pin:
            return ((4.2*self.battery_pin.read())/4095)*2
        return 0

    
    def green_led_battery_controller(self):
        bat_voltage = self.get_battery_voltage()
        if bat_voltage == 0:
            self.init_off()
            return
        
        if self.green_1 and self.green_1.value() != 1:
            self.set_pins({"g1": 1})
            
        if bat_voltage >= 3.44:
            if self.green_2.value() != 1:
                time.sleep(0.5)
                self.set_pins({"g2": 1})
        else:
            if self.green_2.value() != 0:
                self.set_pins({"g2": 0})
            
        if bat_voltage >= 3.60:
            if self.green_3.value() != 1:
                time.sleep(0.5)
                self.set_pins({"g3": 1})
        else:
            if self.green_3.value() != 0:
                self.set_pins({"g3": 0})


    def start_fade_loop(self, pwm_pins: list, run):
        # PWM Fade a pin, after initial delay
        for p in pwm_pins:
            p.duty(0)
        time.sleep(3)

        step = self.steps
        if step < 8:
            step = 8

        while run():
            step = self.steps
            for i in range(0, 1024, step):
                # Fade in
                for p in pwm_pins:
                    p.duty(i)
                
                time.sleep(self.delay)
                if not run():
                    break

            time.sleep(self.on_time_mult*self.delay)
            step = self.steps
            for i in range(1023, -1, -step):
                # Fade out                
                for p in pwm_pins:
                    p.duty(i)
                
                time.sleep(self.delay)
                if not run():
                    break
            if i:
                del i
            time.sleep(self.off_time_mult*self.delay)
            if (gc.mem_free() < 41200): #42000
                gc.collect()

        for p in pwm_pins:
            p.duty(0)
    
    def set_delay(self, val: float):
        if val < 0.012:
            val = 0.012
        if val > 10:
            val = 10
        self.delay = val
            
    def set_steps(self, val: int):
        if val < 8:
            val = 8
        if val > 128:
            val = 128
        self.steps = val
    
    def _run_right_led(self):
        # Calling the dict for the values caused a mem leak
        # calling the sub-dict helped, but direct was best
        return self.right_led_enabled
    
    def _run_left_led(self):
        return self.left_led_enabled
    
    def _run_sync_leds(self):
        return (self.sync_leds_enabled and (self._run_right_led() or self._run_left_led()))
    
    def start_left_light(self):
        self.stop_sync_lights()
        if self._run_left_led():
            self.stop_left_light()
            time.sleep((self.on_time_mult*self.delay*2)+0.5+self.off_time_mult*self.delay)
        self.left_led_enabled = True
        th.start_new_thread(self.start_fade_loop, ([self.pwm_pin_d["left_pwm"]], self._run_left_led))
        
    def start_right_light(self):
        self.stop_sync_lights()
        if self._run_right_led():
            self.stop_right_light()
            time.sleep((self.on_time_mult*self.delay*2)+0.5+self.off_time_mult*self.delay)
        self.right_led_enabled = True
        th.start_new_thread(self.start_fade_loop, ([self.pwm_pin_d["right_pwm"]], self._run_right_led))
        
    def start_sync_lights(self):
        # Reset and start at (near enough) same time.
        if self._run_sync_leds():
            self.stop_sync_lights()
            self.stop_right_light()
            self.stop_left_light()
            time.sleep((self.on_time_mult*self.delay*2)+0.5+self.off_time_mult*self.delay)
        self.left_led_enabled = True
        self.right_led_enabled = True
        self.sync_leds_enabled = True
        th.start_new_thread(self.start_fade_loop, ([self.pwm_pin_d["right_pwm"],
                                                   self.pwm_pin_d["left_pwm"]],
                                                   self._run_sync_leds))
        
    def stop_sync_lights(self):
        self.sync_leds_enabled = False
        self._config["leds"]["sync_sides"] = self.sync_leds_enabled
        self.leds = self._config['leds']
        self.stop_right_light()
        self.stop_left_light()

    def stop_right_light(self):
        self.sync_leds_enabled = False
        self._config["leds"]["sync_sides"] = self.sync_leds_enabled
        self.right_led_enabled = False
        self._config["leds"]["right"] = self.right_led_enabled
        self.leds = self._config['leds']
  
    def stop_left_light(self):
        self.sync_leds_enabled = False
        self._config["leds"]["sync_sides"] = self.sync_leds_enabled
        self.left_led_enabled = False
        self._config["leds"]["left"] = self.left_led_enabled
        self.leds = self._config['leds']


