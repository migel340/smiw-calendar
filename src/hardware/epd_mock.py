from PIL import Image
from datetime import datetime
from pathlib import Path
from src.config import OUTDIR, EPD_WIDTH, EPD_HEIGHT


def display(image: Image.Image):
    Path(OUTDIR).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path(OUTDIR) / f"frame-{ts}.png"
    image.convert("1").save(path)
    image.show()


class EPD:
    width = EPD_WIDTH
    height = EPD_HEIGHT

    def __init__(self):
        pass

    def clear(self):
        pass

    def init(self):
        pass

    def display(self, image: Image.Image):
        display(image)

    def sleep(self):
        pass