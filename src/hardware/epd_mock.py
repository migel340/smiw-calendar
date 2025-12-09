from PIL import Image
from datetime import datetime
from pathlib import Path
from src.config import OUTDIR, EPD_WIDTH, EPD_HEIGHT


def display(image: Image.Image):
    # Create parent directories if they don't exist
    Path(OUTDIR).mkdir(parents=True, exist_ok=True)
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

    def Clear(self):
        """Alias for clear() for compatibility."""
        self.clear()

    def init(self):
        pass

    def getbuffer(self, image: Image.Image) -> Image.Image:
        """Convert image to display buffer format."""
        return image.convert("1")

    def display(self, image: Image.Image):
        display(image)

    def display_partial(self, image: Image.Image):
        """Partial refresh - in mock just calls normal display."""
        display(image)

    def sleep(self):
        pass