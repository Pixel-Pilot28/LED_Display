"""LGBGr9j84KlTovyAeFBuGq5AuXuZeomg
"""

import os
import json
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from threading import Thread

class NYTApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.api_key = 'LGBGr9j84KlTovyAeFBuGq5AuXuZeomg'  # Replace with your NYT API key
        self.cache_path = "/home/pi/Projects/Display/py_cache/nyt_cache.json"
        self.font_banner = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        self.font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
        self.font_category = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
        self.banner_color = (255, 0, 0)
        self.text_color = (255, 255, 255)
        self.category_color = (0, 255, 255)  # Cyan color for category text
        self.scroll_speed = 2
        self.story_cycle_time = 10  # seconds

    def fetch_headlines(self, url):
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('results', [])
        headlines = [{'title': article['title'], 'category': article['section']} for article in articles if article['title'].isascii()]
        with open(self.cache_path, 'w') as f:
            json.dump(headlines, f)
        return headlines

    def fetch_top_stories(self):
        url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/1.json?api-key={self.api_key}"
        return self.fetch_headlines(url)

    def fetch_breaking_news(self):
        url = f"https://api.nytimes.com/svc/news/v3/content/all/all.json?api-key={self.api_key}"
        return self.fetch_headlines(url)

    def load_headlines(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        return []

    def update_headlines(self):
        while True:
            try:
                self.fetch_breaking_news()
                time.sleep(420)  # Update every 7 minutes
                self.fetch_top_stories()
                time.sleep(180)  # Show top stories for 3 minutes
            except Exception as e:
                print(f"Error fetching headlines: {e}")
                time.sleep(600)  # Wait before retrying if an error occurs

    def draw_banner(self, draw, banner_text, banner_color):
        draw.rectangle((0, 0, 64, 9), fill=banner_color)
        draw.text((1, -1), banner_text, font=self.font_banner, fill=self.text_color)

    def draw_headline(self, draw, category, title, offset):
        headline = f"{category} | {title}"
        width, _ = draw.textbbox((0, 0), headline, font=self.font_title)[2:]
        draw.text((64 - offset, 12), headline, font=self.font_title, fill=self.text_color)
        draw.text((64 - offset, 12), category , font=self.font_title, fill=self.category_color)
        return width

    def scroll_headlines(self, headlines, banner_text, banner_color):
        for headline in headlines:
            image = Image.new("RGB", (64, 32))
            draw = ImageDraw.Draw(image)
            draw.fontmode = "1"  # Use single pixel wide lines for text
            self.draw_banner(draw, banner_text, banner_color)
            width = self.draw_headline(draw, headline['category'], headline['title'], 0)
            for offset in range(64 + width):
                image = Image.new("RGB", (64, 32))
                draw = ImageDraw.Draw(image)
                draw.fontmode = "1"  # Use single pixel wide lines for text
                self.draw_banner(draw, banner_text, banner_color)
                self.draw_headline(draw, headline['category'], headline['title'], offset)
                self.display_controller.set_image(image)
                time.sleep(0.05)

    def run(self):
        Thread(target=self.update_headlines, daemon=True).start()
        while True:
            headlines = self.load_headlines()
            if not headlines:
                headlines = self.fetch_breaking_news()
            start_time = time.time()
            while time.time() - start_time < 420:
                self.scroll_headlines(headlines, "NYT Wire:", (255, 0, 0))
            headlines = self.fetch_top_stories()
            self.scroll_headlines(headlines, "Top Stories:", (0, 0, 255))
