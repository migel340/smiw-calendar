"""
Events Tomorrow Screen - displays tomorrow's calendar events.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from src.app.screens.base_screen import BaseScreen
from src.hardware import get_epd
from src.config import FONT_PATH
from src.graphics.draw_utils import text_wraper
from src.services.ollama_service import random_joke

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


class JokeScreen(BaseScreen):
    """Screen displaying a random joke."""
    
    def __init__(self):
        super().__init__(name="Joke Screen")
        self._joke: Optional[str] = None
    
    def get_data(self) -> dict:
        """Generate random joke."""
        try:
            self._joke = random_joke()
            logger.info("Generated a random joke")
        except Exception as e:
            logger.exception("Failed to generate a random joke: %s", e)
            self._joke = None
        return {"joke": self._joke}
    
    def render(self) -> Image.Image:
        """Render joke screen."""
        epd = get_epd()
        img = Image.new("1", (epd.width, epd.height), 1)
        draw = ImageDraw.Draw(img)
        
        font_small = _load_font(size=12)
        font_large = _load_font(size=14)
        
        y_offset = 5
        line_height = 16
        
        # Header
        draw.text((5, y_offset), "RANDOM JOKE", fill=0, font=font_large)
        y_offset += line_height + 2
        
        if not self._joke:
            draw.text((5, y_offset), "No joke available", fill=0, font=font_small)
            return img
        
        wrapped = text_wraper(self._joke, draw, font_small, epd.width - 10)
        for line in wrapped:
            if y_offset > epd.height - line_height:
                break
            draw.text((5, y_offset), line, fill=0, font=font_small)
            y_offset += line_height
        return img
    
    def on_enter(self) -> None:
        """Refresh data when entering this screen."""
        logger.info("Entering Joke screen")
        self.get_data()
