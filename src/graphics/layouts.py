
from pydoc import text
from re import L
from src.hardware import get_epd
from PIL import Image, ImageDraw, ImageFont
from src.app.screens import get_structured_tasks, get_events_today_and_tomorrow
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


def draw_events_screen(events: List[Dict[str, Any]]) -> Image.Image:
    epd = get_epd()
    img = Image.new("1", (epd.width, epd.height), 1)
    draw = ImageDraw.Draw(img)
    
    all_day_events: List[Dict[str, Any]] = []
    timed_events: List[Dict[str, Any]] = []

    font_small = _load_font(size=12)
    font_large = _load_font(size=14)
    
    y_offset = 5
    line_height = 16

    for event in events:
        is_all_day = bool(event.get("is_all_day", False))
        if is_all_day:
            all_day_events.append(event)
        else:
            timed_events.append(event)

    draw.text((5, y_offset), "EVENTS", fill=0, font=font_large)
    y_offset += line_height


    if all_day_events:
        draw.text((5, y_offset), "All Day:", fill=0, font=font_large)
        y_offset += line_height
        for event in all_day_events:
            title = event.get("title")
            title_string = f"* {title}"
            wrapped_title = text_wraper(title_string, draw, font_small, epd.width - 10)
            for line in wrapped_title:
                draw.text((5, y_offset), line, fill=0, font=font_small)
                y_offset += line_height

    if timed_events:
        draw.text((5, y_offset), "Timed:", fill=0, font=font_large)
        y_offset += line_height
        for event in timed_events:
            title = event.get("title")
            start = event.get("start")
            end = event.get("end")

            title_string = f"* {title}"
            wrapped_title = text_wraper(title_string, draw, font_small, epd.width - 10)
            for line in wrapped_title:
                draw.text((5, y_offset), line, fill=0, font=font_small)
                y_offset += line_height

            if start:
                start_val = start if isinstance(start, str) else str(start)
                end_val = end if isinstance(end, str) else str(end)
                start_string = f"{start_val} - {end_val}"
                wrapped_start = text_wraper(start_string, draw, font_small, epd.width - 15)
                for line in wrapped_start:
                    draw.text((10, y_offset), line, fill=0, font=font_small)
                    y_offset += line_height

    return img



def draw_dht11(temperature: float, humidity: float) -> Image.Image:
    try:
        epd = get_epd()
        img = Image.new("1", (epd.width, epd.height), 1)
        draw = ImageDraw.Draw(img)

        font_small = _load_font(size=14)
        font_large = _load_font(size=24)
        draw.text((5, 5), "DHT11", fill=0, font=font_large)
        draw.text((5, 40), "Temperature:", fill=0, font=font_small)
        draw.text((15, 60), f"{temperature:.1f} °C", fill=0, font=font_small)
        draw.text((5, 100), "Humidity:", fill=0, font=font_small)
        draw.text((15, 120), f"{humidity:.1f} %", fill=0, font=font_small)

        return img
    except Exception as e:
        logger.exception("Error drawing DHT11 data: %s", e)

if __name__ == "__main__":

    epd = get_epd()
    epd.init()
    
    # logger.info("Testing draw_tasks_screen...")
    # tasks = get_structured_tasks()
    # logger.info("Fetched %d tasks for testing", len(tasks))
    # img = draw_tasks_screen(tasks)
    

    # epd.display(img)

    # logger.info("Testing draw_events_screen...")

    # logger.info("Testing draw_dht11...")
    # img = draw_dht11(23.5, 45.0)
    # epd.display(img)    
    events = get_events_today_and_tomorrow()
    logger.info("Fetched %d events for testing (today/tomorrow only)", len(events))
    img = draw_events_screen(events)
    epd.display(img)
