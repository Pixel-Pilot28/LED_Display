import time
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta

class FinanceApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.portfolio = {GE, VXUS}  # Holds the user's portfolio
        self.api_url = "https://api.example.com/stock"  # Replace with actual API URL
        self.api_key = "YOUR_API_KEY"  # Replace with your API key
        self.font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        self.font_banner = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        self.update_interval = 60  # seconds
        self.running = False

    def add_to_portfolio(self, symbol, quantity):
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity

    def fetch_stock_data(self, symbol):
        try:
            response = requests.get(f"{self.api_url}/{symbol}", params={"apikey": self.api_key})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return None

    def calculate_portfolio_value(self):
        total_value = 0
        portfolio_value = {}
        for symbol, quantity in self.portfolio.items():
            data = self.fetch_stock_data(symbol)
            if data:
                current_price = data.get("price")
                portfolio_value[symbol] = current_price * quantity
                total_value += portfolio_value[symbol]
        return total_value, portfolio_value

    def get_past_values(self, symbol, period):
        # Placeholder for historical data fetching
        # You need to implement this method based on the financial data API you use
        return []

    def calculate_performance(self):
        performance = {}
        for symbol in self.portfolio.keys():
            performance[symbol] = {}
            current_price = self.fetch_stock_data(symbol).get("price")
            for period in ["hour", "day", "week", "month", "six_months", "year", "three_years"]:
                past_prices = self.get_past_values(symbol, period)
                if past_prices:
                    initial_price = past_prices[0]
                    performance[symbol][period] = ((current_price - initial_price) / initial_price) * 100
        return performance

    def draw_info(self, draw, text, y_offset, color):
        draw.text((1, y_offset), text, font=self.font_info, fill=color)

    def display_performance(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        performance = self.calculate_performance()
        y_offset = 0
        for symbol, periods in performance.items():
            for period, change in periods.items():
                color = (0, 255, 0) if change > 0 else (255, 0, 0)
                text = f"{symbol} ({period}): {change:.2f}%"
                self.draw_info(draw, text, y_offset, color)
                y_offset += 10
                if y_offset >= 32:
                    self.display_controller.set_image(image)
                    time.sleep(3)
                    y_offset = 0
                    image = Image.new("RGB", (64, 32))
                    draw = ImageDraw.Draw(image)
        self.display_controller.set_image(image)

    def run(self):
        self.running = True
        while self.running:
            total_value, portfolio_value = self.calculate_portfolio_value()
            print(f"Total Portfolio Value: {total_value}")
            self.display_performance()
            time.sleep(self.update_interval)

    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    display_controller = DisplayController()  # Assume DisplayController is defined elsewhere
    app = FinanceApp(display_controller)
    app.add_to_portfolio("AAPL", 10)
    app.add_to_portfolio("GOOGL", 5)
    app.run()
