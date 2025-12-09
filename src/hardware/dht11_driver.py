import time
from typing import Any, Optional, NamedTuple
import logging
import random
import os

logger = logging.getLogger(__name__)

# DHT11 Pin - default GPIO 22 (physical pin 15)
# You can override via env var DHT_PIN (either integer BCM number or board pin name like 'D4')
DHT_PIN_ENV = os.getenv("DHT_PIN")
try:
    DHT_PIN = int(DHT_PIN_ENV) if DHT_PIN_ENV is not None else 22
except Exception:
    DHT_PIN = DHT_PIN_ENV or 22

# Backends: try Adafruit_DHT (legacy) first, then CircuitPython adafruit_dht
_BACKEND = None
_HAS_ADAFRUIT_DHT = False
_HAS_CIRCUITPY = False
Adafruit_DHT = None
adafruit_dht = None
board = None
try:
    import Adafruit_DHT
    _HAS_ADAFRUIT_DHT = True
    _BACKEND = "adafruit_legacy"
except Exception:
    try:
        import board
        import adafruit_dht
        _HAS_CIRCUITPY = True
        _BACKEND = "circuitpython"
    except Exception as e:
        logger.warning("DHT11 hardware not available (no supported library): %s", e)

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
    """Real DHT11 sensor wrapper supporting both Adafruit_DHT and adafruit_dht backends."""

    def __init__(self, pin: Any):
        self.pin = pin
        self.backend = _BACKEND
        self._device = None
        logger.info("Initializing DHT11 backend=%s pin=%s", self.backend, pin)

        if self.backend == "adafruit_legacy":
            # Adafruit_DHT works with BCM integer pin numbers
            self.sensor = Adafruit_DHT.DHT11
        elif self.backend == "circuitpython":
            # Try to resolve board pin object from numeric or string
            board_pin = None
            try:
                if isinstance(pin, int):
                    board_pin = getattr(board, f"D{pin}", None)
                else:
                    # allow passing 'D4' or 'GPIO22'
                    board_pin = getattr(board, str(pin), None)
            except Exception:
                board_pin = None

            if board_pin is None:
                # fallback: try common D4
                board_pin = getattr(board, "D4", None)
                logger.warning("Could not resolve board pin for DHT11; falling back to D4")

            try:
                # use_pulseio=False is recommended on Raspberry Pi
                self._device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
            except Exception as e:
                logger.exception("Failed to create adafruit_dht DHT11 device: %s", e)
                self._device = None

    def read(self, retries: int = 5, delay: float = 2.0) -> Optional[DHTReading]:
        if self.backend == "adafruit_legacy":
            # Use Adafruit_DHT.read_retry which handles retries internally
            try:
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, int(self.pin), retries=retries, delay_seconds=int(delay))
                if humidity is not None and temperature is not None:
                    return DHTReading(float(temperature), float(humidity))
            except Exception as e:
                logger.warning("Adafruit_DHT read error: %s", e)
            return None

        elif self.backend == "circuitpython":
            # adafruit_dht raises RuntimeError for transient errors; retry a few times
            if self._device is None:
                logger.warning("CircuitPython DHT device not initialized")
                return None

            for attempt in range(retries):
                try:
                    temp = self._device.temperature
                    hum = self._device.humidity
                    if temp is not None and hum is not None:
                        return DHTReading(float(temp), float(hum))
                except RuntimeError as e:
                    logger.debug("DHT read transient error (attempt %d/%d): %s", attempt + 1, retries, e)
                except Exception as e:
                    logger.exception("DHT read unexpected error: %s", e)
                    return None

                time.sleep(delay)
            return None

        else:
            logger.warning("No DHT backend available")
            return None


def _initialize_dht11() -> Optional[Any]:
    # If neither backend is available, use mock
    if _BACKEND is None:
        logger.info("Using mock DHT11 sensor")
        return _MockDHT11()

    try:
        return _RealDHT11(DHT_PIN)
    except Exception as exc:
        logger.exception("Failed to initialize DHT11: %s", exc)
        return None


def read_dht11(dht_device: Any) -> Optional[DHTReading]:
    """Read from DHT11 device wrapper."""
    try:
        # Some implementations expose .read(), others are wrapper objects
        if hasattr(dht_device, "read"):
            return dht_device.read()
        # Fallback: if object provides temperature/humidity properties
        if hasattr(dht_device, "temperature") and hasattr(dht_device, "humidity"):
            t = getattr(dht_device, "temperature")
            h = getattr(dht_device, "humidity")
            if t is not None and h is not None:
                return DHTReading(float(t), float(h))
        return None
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
