from time import sleep
from typing import Optional, Any
import threading
import logging

try:
    from gpiozero import LED 
    _HAVE_GPIOZERO = True
except Exception:
    LED = None
    _HAVE_GPIOZERO = False

logger = logging.getLogger(__name__)

LED_PIN = 18

class _MockLED:

    def __init__(self, pin: int):
        self.pin = pin
        self._state = False
        logger.info("[MOCK] LED(%s) created", pin)

    def on(self) -> None:
        self._state = True
        logger.info("[MOCK] LED ON")

    def off(self) -> None:
        self._state = False
        logger.info("[MOCK] LED OFF")

    def close(self) -> None:
        logger.info("[MOCK] LED closed")


LED_CLASS: Any = LED if _HAVE_GPIOZERO else _MockLED

_led: Optional[Any] = None
_lock = threading.Lock()


def _get_led() -> Any:

    global _led, LED_CLASS
    with _lock:
        if _led is None:
            try:
                _led = LED_CLASS(LED_PIN)
            except Exception as e:
                logger.warning("Failed to create real LED (%s); falling back to mock: %s", LED_PIN, e)
                LED_CLASS = _MockLED
                _led = LED_CLASS(LED_PIN)
    return _led


def turn_on() -> None:
    try:
        _get_led().on()
    except Exception:
        logger.exception("Failed to turn on LED")


def turn_off() -> None:
    try:
        _get_led().off()
    except Exception:
        logger.exception("Failed to turn off LED")


def cleanup() -> None:
    global _led
    with _lock:
        if _led is not None:
            try:
                _led.close()
            except Exception:
                logger.exception("Error while closing LED")
            _led = None


if __name__ == "__main__":
    try:
        while True:
            turn_on()
            print("LED ON")
            sleep(1)
            turn_off()
            print("LED OFF")
            sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        cleanup()
        print("Program terminated")
