import sys
import os
import logging
from src.hardware.waveshare_lib import epd2in13_V4
from PIL import Image

from src.config import EPD_WIDTH, EPD_HEIGHT
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)



logger = logging.getLogger(__name__)


class EPD:

    width = EPD_WIDTH
    height = EPD_HEIGHT

    def __init__(self):
        self._hw = None

    def _ensure_hw(self):
        if self._hw is None:
            try:
                self._hw = epd2in13_V4.EPD()
                self._hw.init()
                try:
                    self._hw.Clear(0xFF)
                except Exception:
                    logger.debug("EPD Clear() not available or failed")
            except Exception:
                logger.exception("Failed to initialize hardware EPD")
                self._hw = None

    def init(self):
        self._ensure_hw()

    def clear(self):
        if self._hw:
            try:
                self._hw.Clear(0xFF)
            except Exception:
                logger.exception("Failed to clear EPD")

    def Clear(self):
        """Alias for clear() for compatibility."""
        self.clear()

    def getbuffer(self, image: Image.Image) -> bytes:
        """Convert image to display buffer format."""
        self._ensure_hw()
        if self._hw:
            return self._hw.getbuffer(image.convert("1"))
        return image.convert("1").tobytes()

    def display(self, image_or_callable):
        image = None
        if callable(image_or_callable):
            try:
                image = image_or_callable()
            except TypeError:
                image = image_or_callable(self)
            except Exception:
                logger.exception("Callable provided to display() raised an exception")
                raise
        else:
            image = image_or_callable

        if not isinstance(image, Image.Image):
            raise TypeError("display() expects a PIL Image or callable returning Image")


        try:
            img = image.convert("1")
        except Exception:
            img = Image.frombytes("1", image.size, image.tobytes())

        
        if img.size != (self.width, self.height):
            try:
                img = img.resize((self.width, self.height))
            except Exception:
                logger.exception("Failed to resize image to EPD dimensions")


        self._ensure_hw()

        if self._hw:
            try:
                buf = self._hw.getbuffer(img)
                self._hw.display(buf)
                return
            except Exception:
                logger.exception("Hardware display failed")

       
        logger.error("EPD hardware not available or display failed; cannot show image on device")
        raise RuntimeError("EPD hardware not available or display failed")

    def sleep(self):
        if self._hw:
            try:
                if hasattr(self._hw, "sleep"):
                    self._hw.sleep()
                elif hasattr(self._hw, "Sleep"):
                    self._hw.Sleep()
            except Exception:
                logger.exception("Failed to put EPD to sleep")
