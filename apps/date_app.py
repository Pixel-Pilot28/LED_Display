from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class DateApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

    def run(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        draw.rectangle((-1, -1, 64, 32), outline=0, fill=(229, 117, 31))
        draw.fontmode = "1"  # Use single pixel wide lines for text
        current_date = datetime.now().strftime("%m-%d-%y")
        current_shortdate = datetime.now().strftime("%a %b,%d")
        draw.text((3, 1), current_shortdate, font=self.font, fill="#D7D2CB")
        draw.text((8, 12), current_date, font=self.font, fill="#D7D2CB")
        self.display_controller.set_image(image)
