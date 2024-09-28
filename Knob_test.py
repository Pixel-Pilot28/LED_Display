import time
import board
import busio
from adafruit_ads7830.ads7830 import ADS7830
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import seesaw, rotaryio, digitalio

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS7830 (Potentiometer ADC)
ads = ADS7830(i2c)

# Initialize Seesaw for Rotary Encoder
ss = Seesaw(i2c, addr=0x36)
encoder = rotaryio.IncrementalEncoder(ss)

# Configure seesaw pin used to read knob button presses
ss.pin_mode(24, ss.INPUT_PULLUP)
button = digitalio.DigitalIO(ss, 24)
button_held = False

last_position = None

def read_ads7830_channel(channel, samples=10):
    values = []
    for _ in range(samples):
        value = ads.read(channel)
        values.append(value)
        time.sleep(0.01)
    return sum(values) // len(values)  # Return the average value

def scale_value(value, from_min, from_max, to_min, to_max):
    # Scale a value from one range to another
    return (value - from_min) * (to_max - to_min) // (from_max - from_min) + to_min

try:
    while True:
        # Read potentiometer value from channel 1 (A1)
        raw_pot_value = read_ads7830_channel(1)
        # Scale potentiometer value to range 0-255 for brightness control
        pot_value = scale_value(raw_pot_value, 0, 65535, 10, 255)

        # Read on/off switch value from channel 2 (A2)
        raw_onoff_value = read_ads7830_channel(2)
        onoff_value = "Off" if raw_onoff_value > 10 else "On"

        # Read rotary encoder position
        position = encoder.position

        if last_position is None or position != last_position:
            last_position = position
            print(f"Encoder Position: {position}")

        if not button.value and not button_held:
            button_held = True
            print("Button pressed")

        if button.value and button_held:
            button_held = False
            print("Button released")

        print(f"Pot raw: {pot_value}({raw_pot_value}) | On/Off: {onoff_value}({raw_onoff_value})")

        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")