'''
http://192.168.1.132:8080/data/aircraft.json

'''

import os
import json
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from threading import Thread
import math

class FlightApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.local_data_url = "http://192.168.1.132:8080/data/aircraft.json"  # Update with your local URL
        self.api_url = "https://api.hexdb.io/v1/aircraft"
        self.api_key = "YOUR_API_KEY"  # Replace with your API key
        self.bounding_box = {'lat_min': 40.0, 'lat_max': 45.0, 'lon_min': -75.0, 'lon_max': -70.0}
        self.font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        self.font_banner = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        self.info_color = (255, 255, 255)
        self.banner_color = (0, 0, 255)
        self.emergency_color = (255, 0, 0)
        self.metric_color = (0, 255, 255)  # Cyan color for the metric
        self.update_interval = 10 # seconds
        self.data_source = "local"  # or "api"
        self.running = False
        self.antenna_location = {'lat': 38.8951, 'lon': -77.0364}  # Example: Washington, D.C.

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon1 - lon2)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def fetch_local_data(self):
        try:
            response = requests.get(self.local_data_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching local data: {e}")
            return {}

    def fetch_api_data(self):
        params = {
            'apikey': self.api_key,
            'lat_min': self.bounding_box['lat_min'],
            'lat_max': self.bounding_box['lat_max'],
            'lon_min': self.bounding_box['lon_min'],
            'lon_max': self.bounding_box['lon_max']
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching API data: {e}")
            return {}

    def fetch_data(self):
        if self.data_source == "local":
            return self.fetch_local_data()
        else:
            return self.fetch_api_data()

    def lookup_hex(self, hex_code):
        url = f"https://api.hexdb.io/v1/aircraft/{hex_code}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error looking up hex code {hex_code}: {e}")
            return {}

    def process_data(self, data):
        aircraft = data.get('aircraft', [])
        closest, highest, fastest = None, None, None
        min_distance, max_altitude, max_speed = float('inf'), float('-inf'), float('-inf')
        emergency_aircraft = None

        print(f"Processing {len(aircraft)} aircraft")

        for ac in aircraft:
            lat = ac.get('lat')
            lon = ac.get('lon')
            altitude = ac.get('alt_baro') or ac.get('alt_geom')
            speed = ac.get('gs')
            squawk = ac.get('squawk')

            if lat is not None and lon is not None:
                distance = self.haversine(self.antenna_location['lat'], self.antenna_location['lon'], lat, lon)
            else:
                distance = None

            if squawk in ["7500", "7600", "7700"]:
                emergency_aircraft = ac
                break

            if distance is not None and distance < min_distance and altitude is not None and speed is not None:
                closest = ac
                min_distance = distance

            if altitude is not None and altitude > max_altitude:
                highest = ac
                max_altitude = altitude

            if speed is not None and speed > max_speed:
                fastest = ac
                max_speed = speed

        # If any metric is None, look for the next best aircraft with complete data
        if closest is None:
            closest = self.find_next_best(aircraft, 'distance')
        if highest is None:
            highest = self.find_next_best(aircraft, 'altitude')
        if fastest is None:
            fastest = self.find_next_best(aircraft, 'speed')

        return closest, highest, fastest, emergency_aircraft, len(aircraft) if self.data_source == "local" else None

    def find_next_best(self, aircraft, metric):
        best_aircraft = None
        if metric == 'distance':
            min_distance = float('inf')
            for ac in aircraft:
                if ac.get('lat') is not None and ac.get('lon') is not None and ac.get('alt_baro') is not None and ac.get('gs') is not None:
                    distance = self.haversine(self.antenna_location['lat'], self.antenna_location['lon'], ac['lat'], ac['lon'])
                    if distance < min_distance:
                        best_aircraft = ac
                        min_distance = distance
        elif metric == 'altitude':
            max_altitude = float('-inf')
            for ac in aircraft:
                if ac.get('alt_baro') is not None:
                    altitude = ac['alt_baro']
                    if altitude > max_altitude:
                        best_aircraft = ac
                        max_altitude = altitude
        elif metric == 'speed':
            max_speed = float('-inf')
            for ac in aircraft:
                if ac.get('gs') is not None:
                    speed = ac['gs']
                    if speed > max_speed:
                        best_aircraft = ac
                        max_speed = speed
        return best_aircraft

    def draw_banner(self, draw, banner_text, banner_color):
        draw.rectangle((0, 0, 64, 11), fill=banner_color)
        draw.text((1, -1), banner_text, font=self.font_banner, fill=self.info_color)

    def draw_info(self, draw, metric, info, offset):
        metric_width, _ = draw.textbbox((0, 0), metric, font=self.font_info)[2:]
        info_width, _ = draw.textbbox((0, 0), info, font=self.font_info)[2:]
        draw.text((64 - offset, 12), metric, font=self.font_info, fill=self.metric_color)
        draw.text((64 - offset + metric_width, 12), info, font=self.font_info, fill=self.info_color)
        return metric_width + info_width

    def scroll_info(self, metric, info, banner_text, banner_color):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        draw.fontmode = "1"  # Use single pixel wide lines for text
        self.draw_banner(draw, banner_text, banner_color)
        width = self.draw_info(draw, metric, info, 0)
        for offset in range(64 + width):
            image = Image.new("RGB", (64, 32))
            draw = ImageDraw.Draw(image)
            draw.fontmode = "1"  # Use single pixel wide lines for text
            self.draw_banner(draw, banner_text, banner_color)
            self.draw_info(draw, metric, info, offset)
            self.display_controller.set_image(image)
            time.sleep(0.05)

    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.fetch_data()
                closest, highest, fastest, emergency, total_aircraft = self.process_data(data)

                if emergency:
                    emergency_type = {"7500": "Hijacked Aircraft", "7600": "Radio Failure", "7700": "Emergency"}[emergency['squawk']]
                    info = f"{emergency.get('operator', 'N/A')} {emergency.get('type', 'N/A')} {emergency.get('flight', 'N/A')} {emergency.get('gs', 'N/A')}kt {emergency.get('alt_baro', 'N/A')}ft"
                    self.scroll_info(emergency_type, info, "Emergency", self.emergency_color)
                else:
                    if closest:
                        info = f"{closest.get(' | operator', ' |')} {closest.get('type', '')} {closest.get('flight', '')} {closest.get('gs', '')}kt {closest.get('alt_baro', '')}ft"
                        self.scroll_info("Closest Aircraft", info, "Flight Info", self.banner_color)
                    if highest:
                        info = f"{highest.get(' | operator', ' |')} {highest.get('type', '')} {highest.get('flight', '')} {highest.get('gs', '')}kt {highest.get('alt_baro', '')}ft"
                        self.scroll_info("Highest Aircraft", info, "Flight Info", self.banner_color)
                    if fastest:
                        info = f"{fastest.get(' | operator', ' |')} {fastest.get('type', '')} {fastest.get('flight', '')} {fastest.get('gs', '')}kt {fastest.get('alt_baro', '')}ft"
                        self.scroll_info("Fastest Aircraft", info, "Flight Info", self.banner_color)
                    if total_aircraft is not None:
                        self.scroll_info("Total", f": {total_aircraft}", "Flight Info", self.banner_color)

                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in FlightApp: {e}")
                time.sleep(60)  # Wait before retrying if an error occurs

    def stop(self):
        self.running = False
