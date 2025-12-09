"""
Tasks Screen - displays Google Tasks.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
from pathlib import Path
import logging

from src.app.screens.base_screen import BaseScreen
from src.services.structure_parser import get_structured_tasks
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


class TasksScreen(BaseScreen):
    """Screen displaying tasks from Google Tasks."""
    
    def __init__(self):
        super().__init__(name="Tasks")
        self._tasks: List[Dict[str, Any]] = []
    
    def get_data(self) -> dict:
        """Fetch tasks from Google Tasks."""
        try:
            self._tasks = get_structured_tasks()
            logger.info("Fetched %d tasks", len(self._tasks))
        except Exception as e:
            logger.exception("Failed to fetch tasks: %s", e)
            self._tasks = []
        return {"tasks": self._tasks}
    
    def render(self) -> Image.Image:
        """Render tasks screen."""
        epd = get_epd()
        img = Image.new("1", (epd.width, epd.height), 1)
        draw = ImageDraw.Draw(img)
        
        font_small = _load_font(size=12)
        font_large = _load_font(size=14)
        
        y_offset = 5
        line_height = 16
        
        # Header
        draw.text((5, y_offset), "TASKS", fill=0, font=font_large)
        y_offset += line_height + 2
        
        if not self._tasks:
            draw.text((5, y_offset), "No tasks", fill=0, font=font_small)
            return img
        
        for task in self._tasks:
            title = task.get("title", "")
            due = task.get("due")
            
            title_string = f"• {title}"
            wrapped = text_wraper(title_string, draw, font_small, epd.width - 10)
            for line in wrapped:
                if y_offset > epd.height - line_height:
                    break
                draw.text((5, y_offset), line, fill=0, font=font_small)
                y_offset += line_height
            
            if due:
                due_string = f"  Due: {due}"
                if y_offset <= epd.height - line_height:
                    draw.text((10, y_offset), due_string, fill=0, font=font_small)
                    y_offset += line_height
        
        return img
    
    def on_enter(self) -> None:
        """Refresh data when entering this screen."""
        logger.info("Entering Tasks screen")
        self.get_data()
