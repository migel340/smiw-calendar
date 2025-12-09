"""
DHT11 Screen - displays temperature and humidity data.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from pathlib import Path
import logging

from src.app.screens.base_screen import BaseScreen
from src.hardware.dht11_driver import get_dht11_reading, DHTReading
from src.hardware import get_epd
from src.config import FONT_PATH

logger = logging.getLogger(__name__)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load font with fallback to default."""
    try:
        font = Path(FONT_PATH) if FONT_PATH else None
        if font and font.is_file():
            return ImageFont.truetype(str(font), size)
    except Exception as e:
        logger.warning("Error loading font: %s", e)
    return ImageFont.load_default()


class DHT11Screen(BaseScreen):
    """Screen displaying DHT11 sensor data (temperature & humidity)."""
    
    def __init__(self):
        super().__init__(name="DHT11 Sensor")
        self._reading: Optional[DHTReading] = None
    
    def get_data(self) -> dict:
        """Read data from DHT11 sensor."""
        try:
            self._reading = get_dht11_reading()
            if self._reading:
                logger.info("DHT11 reading: %.1f°C, %.1f%%", 
                           self._reading.temperature, self._reading.humidity)
            else:
                logger.warning("Failed to get DHT11 reading")
        except Exception as e:
            logger.exception("Error reading DHT11: %s", e)
            self._reading = None
        
        return {
            "temperature": self._reading.temperature if self._reading else None,
            "humidity": self._reading.humidity if self._reading else None,
        }
    
    def render(self) -> Image.Image:
        """Render DHT11 screen with temperature and humidity."""
        epd = get_epd()
        img = Image.new("1", (epd.width, epd.height), 1)
        draw = ImageDraw.Draw(img)
        
        font_small = _load_font(size=14)
        font_large = _load_font(size=24)
        font_value = _load_font(size=20)
        
        # Header
        draw.text((5, 5), "ENVIRONMENT", fill=0, font=font_large)
        
        if self._reading is None:
            draw.text((5, 50), "Sensor unavailable", fill=0, font=font_small)
            return img
        
        # Temperature section
        draw.text((5, 45), "Temperature:", fill=0, font=font_small)
        draw.text((15, 65), f"{self._reading.temperature:.1f} °C", fill=0, font=font_value)
        
        # Humidity section
        draw.text((5, 100), "Humidity:", fill=0, font=font_small)
        draw.text((15, 120), f"{self._reading.humidity:.1f} %", fill=0, font=font_value)
        
        return img
    
    def on_enter(self) -> None:
        """Refresh data when entering this screen."""
        logger.info("Entering DHT11 screen")
        self.get_data()
