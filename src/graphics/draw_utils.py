from PIL import ImageDraw, ImageFont, Image
from typing import List


def _measure_text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    """Mierzy szerokość tekstu używając textlength lub textbbox."""
    try:
        return int(draw.textlength(text, font=font))  # type: ignore
    except Exception:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]


def text_wraper(string: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Zawija tekst do linii nie przekraczających max_width pikseli.

    Args:
        string: Tekst do zawinięcia
        draw: Obiekt ImageDraw do pomiaru tekstu
        font: Czcionka
        max_width: Maksymalna szerokość linii w pikselach

    Returns:
        Lista zawiniętych linii tekstu
    """
    lines: List[str] = []
    words = string.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        width = _measure_text_width(draw, test_line, font)

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines
