import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you are using an Adafruit HAT/BONNET

matrix = RGBMatrix(options=options)

# Create a blank image for drawing.
image = Image.new("RGB", (64, 32))
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, 64, 32), outline=0, fill=(0, 0, 0))

# Load a font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

# Draw the text
text = "Hello, World!"
draw.text((1, 1), text, font=font, fill="#FFFFFF")

# Display image on the matrix
matrix.SetImage(image.convert('RGB'))

# Keep the display on for 10 seconds to verify
time.sleep(10)
