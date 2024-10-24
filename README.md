# Raspberry Pi LED Display Project

Welcome to the Raspberry Pi LED Display Project! This repository is your one-stop solution for building a fully customizable LED display system powered by a Raspberry Pi. Whether you want to display live soccer scores, real-time news, or flight data, this project will help you bring it to life using a colorful RGB matrix. **Get ready to create a dynamic, smart display right at your fingertips!**

## App List

### 1. **Sports App**
Display real-time scores, schedules, and match details for your favorite teams! This app uses data scraped from ESPN and shows:
- Current game status: live, upcoming, or final.
- Teams' abbreviations and icons.
- Game details such as time, score, and team record (wins, draws, losses).
- Auto-updates every two minutes for live games.

### 2. **News App**
Stay informed with the latest headlines! Using the New York Times API, this app fetches and displays breaking news and top stories on your LED matrix.
- The display will switch between top headlines and breaking news, showing the news category followed by the article title.
- Customizable fonts for titles and news ticker.
- News data locally to a JSON file and updated periodically every 10 minutes to save on API calls.

### 3. **Flight Display App**
Track real-time flight information in your area, using data from a local ADSB listener or external APIs.
- Display nearby aircraft, showing altitude, speed, type, and operator.
- Emergency squawk detection (7500, 7600, 7700) triggers special alerts.
- Configure your data sources (local ADSB listener + web API or just the web API).

### 4. **Weather App**
Switches between a real-time weather display with an hourly outlook and a four-day forecast with basic information 
- Displays current weather with associated icons for different weather types.
- The current weather display will also show the predicted weather over the next few hours.
- The future weather display will show the daily forecast for the next four days.

### 5. **Date and Time App**
A basic app that simply displays the date and time 
- Shows the current date or time.

### 6. **Shutdown Animation**
This fun animation shows when the system is shutting down:
- Text animation with falling rainbow pixels that gradually erase the message. Once the message is erased, the system will shut down.

## Hardware Controls

### 1. **Display Control**
Uses an integrated potentiometer to adjust the brightness of the display and completely turn the display off. 
- While in the "On" position, the voltage data read from the potentiometer will adjust the display's brightness such that turning the potentiometer will adjust the brightness.
- When the potentiometer is switched fully off, the display will turn off while the Raspberry Pi remains on.
- If the potentiometer is switched off and the rotary encoder is depressed, the shutdown animation will begin, and both the display and Raspberry Pi will be shut down.

### 2. **App Switching**
Can turn the rotary encoder to switch between apps.
- Can turn clockwise to move forward or counterclockwise to move backward in the app list.
- NOTE: The entire system will turn off if the display is turned off and the rotary encoder is pressed.

## Hardware Requirements
- **Raspberry Pi** (Model 3 or 4 recommended)
- **RGB LED Matrix Display** (64x32 pixels)
- **Rotary Encoder** and **Potentiometer** for input
- **Optional ADS-B Receiver** for local flight tracking

## Software Requirements
- Python 3.7 or higher
- Pillow (for image rendering)
- Requests (for API calls)
- NYTimes API Key (for News App)
- Openweather API key

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Pixel-Pilot28/LED_Display.git
   cd rpi-led-display
   ```

2. **Install Required Python Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Apps**
   - **Sports App**: Edit `config.json` to add your favorite teams. You can find the correct abbreviations for each team using ESPN’s team API. The app will fetch schedules and live scores based on these settings.
   - **News App**: Insert your New York Times API key in the `nyt_cache.json` file located at `/home/pi/Projects/Display/py_cache/`.
   - **Flight Display App**: If using a local ADS-B antenna, configure the local listener IP in `flight_app.py`. Otherwise, it defaults to using a web API.
   - **Weather App**: Input your location and API OpenWeatherMap key. 

4. **Run the Main Script**
   ```bash
   python main.py
   ```

5. **Enjoy the Display!**
   Use the rotary encoder to navigate through the apps. The potentiometer allows you to control the brightness of the display.

## Team Icon Management
Icons are essential for visualizing team logos in the Sports App. They are dynamically loaded from the folder structure based on team abbreviations:
- Path: `/home/pi/Projects/Display/sport_logos/{team_abbreviation}.bmp`
- The icons are typically 8x8 pixels to fit the matrix size.

If the correct team abbreviation is not found, the code uses ESPN's official team abbreviations to locate and display the correct icon automatically.


## Building the display

1. **Parts List**

**Display**
  - 5V 10A switching power supply: http://www.adafruit.com/product/658
  - Adafruit RGB Matrix Bonnet for Raspberry Pi: http://www.adafruit.com/product/3211
  - Black LED Diffusion Acrylic Panel - 10.2" x 5.1": http://www.adafruit.com/product/4749
  - Raspberry Pi 4 Model B - 4 GB RAM: http://www.adafruit.com/product/4296
  - 64x32 RGB LED Matrix - 4mm pitch: http://www.adafruit.com/product/2278
  - DC Barrel Jack: https://www.aliexpress.us/item/2255799866746420.html
  - Three-pin (power, ground, data) 18 gauge wire: https://www.aliexpress.us/item/2251832088900868.html
  - USB-C OTG breakout: https://www.aliexpress.us/item/3256802067184763.html

**Hardware Controls**
  - Panel Mount Right Angle 10K Linear Potentiometer w/On-Off Switch: http://www.adafruit.com/product/3395
  - Adafruit I2C Stemma QT Rotary Encoder Breakout with Encoder: http://www.adafruit.com/product/5880
  - STEMMA QT / Qwiic JST SH 4-pin to Premium Male Headers Cable: http://www.adafruit.com/product/4209
  - STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long: http://www.adafruit.com/product/4399
  - Adafruit ADS7830 8-Channel 8-Bit ADC with I2C: http://www.adafruit.com/product/5836
  - Slim Rubber Rotary Encoder Knob - 11.5mm x 14.5mm D-Shaft: http://www.adafruit.com/product/5093
  - Potentiometer Knob - Soft Touch T18 - Blue: http://www.adafruit.com/product/2048

**3D-Printed Enclosure**
  - 3D Printing file: https://www.thingiverse.com/thing:6781511
  - M2 and M3 nuts and screws: https://www.aliexpress.us/item/3256805018002859.html

2. **Wiring**

     - Pot to ADS7830
          - gnd-output(A1)-5v(VIN) (the other way would reduce middle pin voltage as you turn it clockwise)
          - Gnd-A2
               - Gnd pin on pot will thus have two wires connecting to it
      - Usb & DC wires to DC port
           - Red usb (V-right) + bare red wire to red center of port ADD SHRINK WRAP
           - green usb (G-left) +bare green wire to the outside of port ADD SHRINK WRAP
     - SEEMA to rgb matrix bonnet
          - Black to GND
          - Red to 5V
          - Blue to SDA
          - Yellow to SCL

## Contributions

Feel free to fork this project, submit issues, or contribute new features. Whether it's adding new apps to the display or improving existing ones, all contributions are welcome.

## License

This project is licensed under the MIT License.
