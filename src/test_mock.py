from PIL import Image, ImageDraw, ImageFont
from src.hardware.epd_mock import display, MockEDP


mock = MockEDP()
img = Image.new("1", (mock.width, mock.height), 1)
draw = ImageDraw.Draw(img)

draw.text((10, 10), "Test Mock", fill=0)

display(img)

