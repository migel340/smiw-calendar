import time
from typing import Any, Optional, NamedTuple
import logging
import random
import os

logger = logging.getLogger(__name__)

# DHT11 Pin - GPIO 22 (physical pin 15)
# Use env var DHT_PIN to override (BCM number)
DHT_PIN_ENV = os.getenv("DHT_PIN")
try:
    DHT_PIN = int(DHT_PIN_ENV) if DHT_PIN_ENV is not None else 22
except Exception:
    DHT_PIN = 22

# Try to import legacy Adafruit_DHT library first, but fall back to CircuitPython
_HAVE_HARDWARE = False
_USE_CIRCUITPY = False
Adafruit_DHT = None
adafruit_dht = None
board = None
try:
    import Adafruit_DHT
    _HAVE_HARDWARE = True
except Exception:
    # Try CircuitPython backend
    try:
        import board
        import adafruit_dht
        _USE_CIRCUITPY = True
        _HAVE_HARDWARE = True
    except Exception as e:
        logger.warning("DHT11 hardware not available, using mock: %s", e)
        Adafruit_DHT = None

_dht11: Optional[Any] = None


class DHTReading(NamedTuple):
    temperature: float
    humidity: float


class _MockDHT11:
    """Mock DHT11 sensor for development/testing."""

    def __init__(self):
        self._base_temp = 22.0
        self._base_humidity = 50.0
        logger.info("[MOCK] DHT11 sensor created")

    def read(self) -> Optional[DHTReading]:
        # Return slightly varying mock values
        temp = self._base_temp + random.uniform(-2.0, 2.0)
        hum = self._base_humidity + random.uniform(-5.0, 5.0)
        return DHTReading(temp, hum)


class _RealDHT11:
    """Real DHT11 sensor wrapper using either Adafruit_DHT or CircuitPython adafruit_dht."""

    def __init__(self, pin: int):
        self.pin = pin
        # If legacy Adafruit_DHT is present, use it
        if Adafruit_DHT is not None:
            self._backend = 'legacy'
            self.sensor = Adafruit_DHT.DHT11
            logger.info("DHT11 (legacy) sensor initialized on GPIO %d", pin)
            self._device = None
        elif _USE_CIRCUITPY:
            self._backend = 'circuitpython'
            # Resolve board pin - common case is board.D4
            try:
                board_pin = getattr(board, f"D{pin}", None) if isinstance(pin, int) else getattr(board, str(pin), None)
            except Exception:
                board_pin = None
            if board_pin is None:
                board_pin = getattr(board, 'D4', None)
            try:
                self._device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
                logger.info("DHT11 (circuitpython) sensor initialized on %s", board_pin)
            except Exception as e:
                logger.exception("Failed to initialize CircuitPython DHT11 device: %s", e)
                self._device = None
        else:
            raise RuntimeError("No DHT backend available")

    def read(self) -> Optional[DHTReading]:
        if getattr(self, '_backend', None) == 'legacy':
            try:
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, int(self.pin), retries=5, delay_seconds=2)
                if humidity is not None and temperature is not None:
                    return DHTReading(float(temperature), float(humidity))
            except Exception as e:
                logger.warning("Adafruit_DHT read error: %s", e)
            return None

        if getattr(self, '_backend', None) == 'circuitpython':
            if self._device is None:
                logger.warning("CircuitPython DHT device not initialized")
                return None
            # Retry loop for transient errors
            for attempt in range(5):
                try:
                    temp = self._device.temperature
                    hum = self._device.humidity
                    if temp is not None and hum is not None:
                        return DHTReading(float(temp), float(hum))
                except RuntimeError as e:
                    logger.debug("DHT read transient error (attempt %d/5): %s", attempt+1, e)
                except Exception as e:
                    logger.exception("DHT read unexpected error: %s", e)
                    return None
                time.sleep(2)
            return None


def _initialize_dht11() -> Optional[Any]:
    if not _HAVE_HARDWARE:
        logger.info("Using mock DHT11 sensor")
        return _MockDHT11()

    try:
        return _RealDHT11(DHT_PIN)
    except Exception as exc:
        logger.exception("Failed to initialize DHT11: %s", exc)
        return None


def read_dht11(dht_device: Any) -> Optional[DHTReading]:
    """
    Read from DHT11.

    The Adafruit_DHT library handles retries internally via read_retry().
    """
    try:
        return dht_device.read()
    except Exception as exc:
        logger.warning("DHT11 read error: %s", exc)
        return None


def get_dht11_reading() -> Optional[DHTReading]:
    global _dht11
    if _dht11 is None:
        _dht11 = _initialize_dht11()
        if _dht11 is None:
            return None

    return read_dht11(_dht11)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    device = _initialize_dht11()
    if device is None:
        print("Failed to initialize DHT11 device. Check wiring and permissions.")
    else:
        print("Reading DHT11 (Ctrl-C to stop)")
        try:
            while True:
                r = read_dht11(device)
                if r is None:
                    print("Failed to get reading from DHT11.")
                else:
                    print(f"Temperature: {r.temperature:.1f}°C, Humidity: {r.humidity:.0f}%")
                time.sleep(2)
        except KeyboardInterrupt:
            print("Exiting...")
