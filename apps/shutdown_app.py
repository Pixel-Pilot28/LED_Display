import threading
import time
import random
import colorsys
import os
from PIL import Image, ImageDraw, ImageFont

class ShutdownApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.matrix = display_controller.matrix
        self.width = self.matrix.width
        self.height = self.matrix.height
        self.pixels = []
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)  # Increased font size
        self.text_color = (255, 255, 255)  # White color for better visibility
        self.background_color = (0, 0, 0)
        self.text = ["Shutting", "down"]  # Separate lines
        self.text_pixels = set()
        self.shutdown_thread = None
        self.running = False

    def create_rainbow_pixel(self):
        hue = random.random()
        r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        return (random.randint(0, self.width - 1), 0, r, g, b)

    def update_pixels(self):
        new_pixels = []
        for x, y, r, g, b in self.pixels:
            if y < self.height - 1:
                new_y = y + 1
                if (x, new_y) in self.text_pixels:
                    self.text_pixels.remove((x, new_y))
                else:
                    new_pixels.append((x, new_y, r, g, b))
        
        # Add new pixels at the top
        new_pixels.extend([self.create_rainbow_pixel() for _ in range(self.width // 4)])
        
        self.pixels = new_pixels

    def get_text_pixels(self):
        image = Image.new("RGB", (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(image)
        draw.fontmode = "1"  # Use single pixel wide lines for text
        text_pixels = set()

        # Calculate total height needed for text
        total_height = sum(draw.textbbox((0, 0), line, font=self.font)[3] for line in self.text)
        y_offset = (self.height - total_height) // 2

        for line in self.text:
            bbox = draw.textbbox((0, 0), line, font=self.font)
            text_width = bbox[2]
            text_height = bbox[3]

            x_position = (self.width - text_width) // 2
            y_position = y_offset

            draw.text((x_position, y_position), line, font=self.font, fill=self.text_color)
            
            for x in range(text_width):
                for y in range(text_height):
                    if image.getpixel((x_position + x, y_position + y)) != self.background_color:
                        text_pixels.add((x_position + x, y_position + y))

            y_offset += text_height

        return text_pixels

    def draw_frame(self):
        image = Image.new("RGB", (self.width, self.height), self.background_color)
        
        for x, y in self.text_pixels:
            image.putpixel((x, y), self.text_color)
        
        for x, y, r, g, b in self.pixels:
            if 0 <= x < self.width and 0 <= y < self.height:
                image.putpixel((x, y), (r, g, b))
        
        self.display_controller.set_image(image)

    def animation_loop(self):
        self.text_pixels = self.get_text_pixels()
        start_time = time.time()

        while self.running and self.text_pixels:
            self.update_pixels()
            self.draw_frame()
            time.sleep(0.05)  # Adjust animation speed as needed

            if time.time() - start_time > 10:  # Set a maximum duration of 10 seconds
                break

        # Clear the display after the animation completes or times out
        self.matrix.Clear()

    def run(self):
        self.running = True
        self.shutdown_thread = threading.Thread(target=self.animation_loop)
        self.shutdown_thread.start()

        # Perform any other shutdown actions if needed
        # print("Shutting Down Test")
        os.system("sudo shutdown now")

    def stop(self):
        self.running = False
        if self.shutdown_thread:
            self.shutdown_thread.join()  # Wait for the thread to complete
