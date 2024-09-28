import os
import time
import json
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from threading import Thread

class WeatherApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.api_key = 'Key'  # Replace with your OpenWeatherMap API key
        self.location = {'lat': xx.xxx, 'lon': xx.xxx}  # Replace with your lat long
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 8)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 7)
        self.icon_path = "/home/pi/Projects/Display/weather_icons_resized"  # Adjust the path as needed
        self.cache_path = "/home/pi/Projects/Display/py_cache/weather_cache.json"  # JSON cache file path
        self.update_interval = 600  # Update weather data every 10 minutes

        # Layout positions
        self.positions = {
            'current_time': (0, 0),
            'current_temp': (0, 23),
            'high_temp': (15, 7),
            'low_temp': (15, 14),
            'humidity': (14, 23),
            'current_icon': (0, 8),
            'hourly_forecast': (28, 0),
            'daily_forecast': (0, 0)
        }

        # Start the background thread for updating weather data
        Thread(target=self.update_weather_data, daemon=True).start()

    def fetch_weather(self):
        lat = self.location['lat']
        lon = self.location['lon']
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=imperial&appid={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def save_weather_data(self, weather_data):
        with open(self.cache_path, 'w') as f:
            json.dump(weather_data, f)

    def load_weather_data(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        return None

    def update_weather_data(self):
        while True:
            try:
                weather_data = self.fetch_weather()
                self.save_weather_data(weather_data)
            except Exception as e:
                print(f"Error fetching weather data: {e}")
            time.sleep(self.update_interval)

    def get_weather_icon(self, icon_code):
        try:
            icon = Image.open(f"{self.icon_path}/{icon_code}.png").convert("RGBA")
            return icon
        except FileNotFoundError:
            return None

    def draw_text(self, draw, position, text, font, fill):
        draw.text(position, text, font=font, fill=fill)

    def display_current_hourly(self, weather_data):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        draw.fontmode = "1"  # Use single pixel wide lines for text

        current = weather_data['current']
        hourly = weather_data['hourly'][:4]  # Display next 4 hours

        current_temp = current['temp']
        high_temp = max([hour['temp'] for hour in hourly])
        low_temp = min([hour['temp'] for hour in hourly])
        weather_icon = current['weather'][0]['icon']
        weather_description = current['weather'][0]['description']
        humidity = current['humidity']
        current_time = datetime.now().strftime("%I:%M")

        # Draw current weather
        self.draw_text(draw, self.positions['current_time'], f"{current_time}", font=self.small_font, fill=(255, 255, 255))
        icon_image = self.get_weather_icon(weather_icon)
        if icon_image:
            image.paste(icon_image, self.positions['current_icon'])
        else:
            self.draw_text(draw, (0, 16), weather_description, font=self.small_font, fill=(255, 255, 255))

        self.draw_text(draw, self.positions['current_temp'], f"{int(current_temp)}°", font=self.font, fill=(255, 255, 255))
        self.draw_text(draw, self.positions['high_temp'], f"{int(high_temp)}", font=self.small_font, fill=(255, 255, 255))
        self.draw_text(draw, self.positions['low_temp'], f"{int(low_temp)}", font=self.small_font, fill=(255, 255, 255))
        self.draw_text(draw, self.positions['humidity'], f"{humidity}%", font=self.small_font, fill=(255, 255, 255))

        # Draw hourly forecast
        for i, hour in enumerate(hourly):
            forecast_time = (datetime.now() + timedelta(hours=i+1)).strftime("%I")
            forecast_temp = hour['temp']
            weather_icon = hour['weather'][0]['icon']
            weather_description = hour['weather'][0]['description']
            icon_image = self.get_weather_icon(weather_icon)

            y_position = self.positions['hourly_forecast'][1] + 8 * i
            self.draw_text(draw, (self.positions['hourly_forecast'][0], y_position), f"{forecast_time}", font=self.small_font, fill=(255, 255, 255))
            if icon_image:
                image.paste(icon_image, (self.positions['hourly_forecast'][0] + 10, y_position))
            else:
                self.draw_text(draw, (self.positions['hourly_forecast'][0] + 10, y_position), weather_description, font=self.small_font, fill=(255, 255, 255))
            self.draw_text(draw, (self.positions['hourly_forecast'][0] + 24, y_position), f"{int(forecast_temp)}°", font=self.small_font, fill=(255, 255, 255))

        self.display_controller.set_image(image)

    def display_daily_forecast(self, weather_data):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        draw.fontmode = "1"  # Use single pixel wide lines for text

        daily = weather_data['daily'][:4]  # Display next 4 days

        # Draw 4-day forecast
        for i, day_data in enumerate(daily):
            day = (datetime.now() + timedelta(days=i)).strftime("%a")
            temp_high = day_data['temp']['max']
            temp_low = day_data['temp']['min']
            pop = day_data.get('pop', 0) * 100  # Probability of precipitation
            weather_icon = day_data['weather'][0]['icon']
            weather_description = day_data['weather'][0]['description']
            icon_image = self.get_weather_icon(weather_icon)

            y_position = self.positions['daily_forecast'][1] + 8 * i
            self.draw_text(draw, (self.positions['daily_forecast'][0], y_position), f"{day}", font=self.small_font, fill=(255, 255, 255))
            if icon_image:
                image.paste(icon_image, (self.positions['daily_forecast'][0] + 15, y_position))
            else:
                self.draw_text(draw, (self.positions['daily_forecast'][0] + 20, y_position), weather_description, font=self.small_font, fill=(255, 255, 255))
            self.draw_text(draw, (self.positions['daily_forecast'][0] + 32, y_position), f"{int(temp_high)}°", font=self.small_font, fill=(255, 255, 255))
            self.draw_text(draw, (self.positions['daily_forecast'][0] + 44, y_position), f"{int(pop)}%", font=self.small_font, fill=(255, 255, 255))

        self.display_controller.set_image(image)

    def run(self):
        while True:
            weather_data = self.load_weather_data()
            if weather_data:
                self.display_current_hourly(weather_data)
                time.sleep(10)  # Display current/hourly for 10 seconds
                self.display_daily_forecast(weather_data)
                time.sleep(10)  # Display daily forecast for 10 seconds
