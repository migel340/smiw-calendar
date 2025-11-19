from threading import Lock
from typing import Any, Optional
import logging

try:
    from gpiozero import Button
except Exception:
    Button = None

logger = logging.getLogger(__name__)

_button: Optional[Any] = None
_pressed_flag = False
_lock = Lock()

if Button is not None:
    try:
        _button = Button(27, pull_up=True, bounce_time=0.05)
    except Exception as exc: 
        logger.exception("Failed to initialize Button: %s", exc)
        _button = None

def _on_pressed() -> None:
    global _pressed_flag
    with _lock:
        _pressed_flag = True

if _button is not None:
    _button.when_pressed = _on_pressed

def button_was_pressed() -> bool:

    global _pressed_flag
    with _lock:
        if _pressed_flag:
            _pressed_flag = False
            return True
        return False

def is_pressed() -> bool:
    if _button is None:
        return False
    try:
        return bool(_button.is_pressed)
    except Exception:
        return False

if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO)

    print("Press the button connected to GPIO 27. Press Ctrl-C to exit.")
    try:
        while True:
            print("Button is pressed:", is_pressed())
            if button_was_pressed():
                print("Button was pressed!")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")