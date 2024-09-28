import board
import busio
from adafruit_ads7830.ads7830 import ADS7830
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio, digitalio
from rgbmatrix import RGBMatrix

class KnobController:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS7830(self.i2c)
        self.ss = Seesaw(self.i2c, addr=0x36)
        self.encoder = rotaryio.IncrementalEncoder(self.ss)
        self.ss.pin_mode(24, self.ss.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(self.ss, 24)

    def read_potentiometer(self, channel, samples=10):
        values = [self.ads.read(channel) for _ in range(samples)]
        return sum(values) // len(values)

    def read_encoder(self):
        return self.encoder.position

    def button_pressed(self):
        return not self.button.value

class DisplayController:
    def __init__(self, matrix: RGBMatrix):
        self.matrix = matrix
        self.display_on = True

    def set_display_on(self, on):
        self.display_on = on
        if not on:
            self.clear()

    def scale_value(self, value, from_min, from_max, to_min, to_max):
        # Scale a value from one range to another
        return (value - from_min) * (to_max - to_min) // (from_max - from_min) + to_min

    def set_brightness(self, raw_value):
        brightness = int((raw_value / 65535) * 255)
        self.matrix.brightness = max(0, min(255, brightness))

    def set_image(self, image):
        self.matrix.SetImage(image)

    def clear(self):
        self.matrix.Clear()
    
    def override_brightness(self, value):
        self.matrix.brightness = value
