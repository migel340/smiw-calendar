"""
Events Today Screen - displays today's calendar events.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
from pathlib import Path
import logging

from src.app.screens.base_screen import BaseScreen
from src.services.structure_parser import get_events_today
from src.hardware import get_epd
from src.config import FONT_PATH
from src.graphics.draw_utils import text_wraper

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


class EventsTodayScreen(BaseScreen):
    """Screen displaying today's events."""
    
    def __init__(self):
        super().__init__(name="Events Today")
        self._events: List[Dict[str, Any]] = []
    
    def get_data(self) -> dict:
        """Fetch today's events from Google Calendar."""
        try:
            self._events = get_events_today()
            logger.info("Fetched %d events for today", len(self._events))
        except Exception as e:
            logger.exception("Failed to fetch today's events: %s", e)
            self._events = []
        return {"events": self._events}
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Return cached events for LED notification checking."""
        return self._events
    
    def render(self) -> Image.Image:
        """Render today's events screen."""
        epd = get_epd()
        img = Image.new("1", (epd.width, epd.height), 1)
        draw = ImageDraw.Draw(img)
        
        font_small = _load_font(size=12)
        font_large = _load_font(size=14)
        
        y_offset = 5
        line_height = 16
        
        # Header
        draw.text((5, y_offset), "TODAY'S EVENTS", fill=0, font=font_large)
        y_offset += line_height + 2
        
        if not self._events:
            draw.text((5, y_offset), "No events today", fill=0, font=font_small)
            return img
        
        # Separate all-day and timed events
        all_day_events = [e for e in self._events if e.get("is_all_day")]
        timed_events = [e for e in self._events if not e.get("is_all_day")]
        
        # Draw all-day events
        if all_day_events:
            draw.text((5, y_offset), "All Day:", fill=0, font=font_large)
            y_offset += line_height
            for event in all_day_events:
                title = event.get("title", "")
                title_string = f"• {title}"
                wrapped = text_wraper(title_string, draw, font_small, epd.width - 10)
                for line in wrapped:
                    if y_offset > epd.height - line_height:
                        break
                    draw.text((5, y_offset), line, fill=0, font=font_small)
                    y_offset += line_height
        
        # Draw timed events
        if timed_events:
            draw.text((5, y_offset), "Timed:", fill=0, font=font_large)
            y_offset += line_height
            for event in timed_events:
                title = event.get("title", "")
                start = event.get("start", "")
                end = event.get("end", "")
                
                title_string = f"• {title}"
                wrapped = text_wraper(title_string, draw, font_small, epd.width - 10)
                for line in wrapped:
                    if y_offset > epd.height - line_height:
                        break
                    draw.text((5, y_offset), line, fill=0, font=font_small)
                    y_offset += line_height
                
                if start:
                    time_str = f"  {start}" + (f" - {end}" if end else "")
                    if y_offset <= epd.height - line_height:
                        draw.text((10, y_offset), time_str, fill=0, font=font_small)
                        y_offset += line_height
        
        return img
    
    def on_enter(self) -> None:
        """Refresh data when entering this screen."""
        logger.info("Entering Events Today screen")
        self.get_data()
