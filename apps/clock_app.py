from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class ClockApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

    def run(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        draw.fontmode = "1"  # Use single pixel wide lines for text
        draw.rectangle((-1, -1, 64, 32), outline=0, fill=(0, 76, 151))
        current_time = datetime.now().strftime("%H:%M:%S")
        current_time12 = datetime.now().strftime("%I:%M %p")
        draw.text((6, 1), current_time12, font=self.font, fill="#40A829")
        draw.text((8, 12), current_time, font=self.font, fill="#40A829")
        self.display_controller.set_image(image)
