
from src.hardware import get_epd
from PIL import Image, ImageDraw, ImageFont
from src.app.screens import get_structured_events, get_structured_tasks
from typing import List, Dict, Any
from src.config import FONT_PATH
from pathlib import Path
from src.graphics.draw_utils import text_wraper
import logging

logger = logging.getLogger(__name__)

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        font = Path(FONT_PATH)
        if not font.is_file():
            logger.warning(f"Font '{font}' not found. Using default font.")
            return ImageFont.load_default()
    except Exception as e:
        logger.error("Error loading font: %s", e)
        return ImageFont.load_default()
    return ImageFont.truetype(str(font), size)

def draw_tasks_screen(tasks: List[Dict[str, Any]]) -> Image.Image:
    epd = get_epd()
    img = Image.new("1", (epd.width, epd.height), 1)
    draw = ImageDraw.Draw(img)

    font_small = _load_font(size=12)
    font_large = _load_font(size=14)
    y_offset = 5
    line_height = 16
    draw.text((5, y_offset), "TASKS", fill=0, font=font_large)\

    y_offset += line_height

    for task in tasks:
        due = task.get("due")
        title = task.get("title")

        if not due:
            title_string = f"* {title}"

            wrapped_lines = text_wraper(title_string, draw, font_small, epd.width - 10)
            for line in wrapped_lines:
                draw.text((5, y_offset), line, fill=0, font=font_small)
                y_offset += line_height

        elif due:
            title_string = f"* {title}"
            due_string = f"- {due}"

            wrapped_title = text_wraper(title_string, draw, font_small, epd.width - 10)
            for line in wrapped_title:
                draw.text((5, y_offset), line, fill=0, font=font_small)
                y_offset += line_height

                wrapped_due = text_wraper(due_string, draw, font_small, epd.width - 15)
            for line in wrapped_due:
                draw.text((10, y_offset), line, fill=0, font=font_small)
                y_offset += line_height
    return img


def test_draw_tasks_screen():
    logger.info("Testing draw_tasks_screen...")
    tasks = get_structured_tasks()
    logger.info("Fetched %d tasks for testing", len(tasks))
    img = draw_tasks_screen(tasks)
    epd = get_epd()
    epd.init()
    epd.display(img)
    logger.info("Displayed tasks screen for testing")

if __name__ == "__main__":
    test_draw_tasks_screen()