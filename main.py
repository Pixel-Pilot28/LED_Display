import os
import time
import threading
from datetime import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from driver import KnobController, DisplayController
from apps.clock_app import ClockApp
from apps.date_app import DateApp
from apps.nyt_app import NYTApp
from apps.weather_app import WeatherApp
from apps.shutdown_app import ShutdownApp
from apps.flight_app import FlightApp
from apps.finance_app import FinanceApp
from apps.soccer_app import SoccerApp

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4

matrix = RGBMatrix(options=options)
display_controller = DisplayController(matrix)
knob_controller = KnobController()

apps = [
    # NYTApp(display_controller),
    WeatherApp(display_controller),
    # ClockApp(display_controller),
    # DateApp(display_controller),
    # FlightApp(display_controller),
    # ShutdownApp(display_controller),
    # FinanceApp(display_controller),
    # SoccerApp(display_controller),
]
current_app_index = 0
display_on = True
last_encoder_position = knob_controller.read_encoder()
app_paused = False  # Flag to indicate if the current app is paused

def run_current_app():
    global app_paused
    while True:
        if display_on and not app_paused:
            apps[current_app_index].run()
        else:
            display_controller.clear()
            time.sleep(1)

def update_brightness():
    raw_pot_value = knob_controller.read_potentiometer(1)
    scaled_value = display_controller.scale_value(raw_pot_value, 0, 255, 0, 100)
    display_controller.set_brightness(scaled_value)

def shutdown_pi():
    print("Shutting down...")
    shutdown_app = ShutdownApp(display_controller)
    shutdown_app.run()

def switch_app(direction):
    global current_app_index
    if direction > 0:
        current_app_index = (current_app_index + 1) % len(apps)
    else:
        current_app_index = (current_app_index - 1) % len(apps)
    print(f"Switched to app index: {current_app_index}")

if __name__ == "__main__":
    try:
        # Run the current app in a separate thread
        app_thread = threading.Thread(target=run_current_app)
        app_thread.start()

        while True:
            # Read on/off switch value from channel 2 (A2)
            raw_onoff_value = knob_controller.read_potentiometer(2)
            onoff_value = raw_onoff_value < 10

            if not onoff_value:
                if display_on:
                    display_on = False
                    display_controller.clear()
                    print("Display off")
                time.sleep(0.5)
                # Check if button is pressed to shutdown
                if knob_controller.button_pressed():
                    shutdown_pi()
                continue
            else:
                if not display_on:
                    display_on = True
                    print("Display on")

            update_brightness()

            # Check for encoder button press to pause/resume app
            if knob_controller.button_pressed():
                app_paused = not app_paused
                if app_paused:
                    print("App paused")
                    display_controller.clear()
                else:
                    print("App resumed")

            # Check for encoder changes to switch apps
            current_encoder_position = knob_controller.read_encoder()
            if current_encoder_position != last_encoder_position:
                direction = current_encoder_position - last_encoder_position
                if app_paused:
                    switch_app(direction)
                    app_paused = False  # Resume app after switching
                    print("App resumed after switching")
                last_encoder_position = current_encoder_position

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting...")
