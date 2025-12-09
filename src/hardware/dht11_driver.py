import time
from typing import Any, Optional, NamedTuple
import logging
import random

logger = logging.getLogger(__name__)

# Try to import hardware libraries, fall back to mock
_HAVE_HARDWARE = False
try:
    import board
    import adafruit_dht
    _HAVE_HARDWARE = True
except (ImportError, NotImplementedError) as e:
    logger.warning("DHT11 hardware not available, using mock: %s", e)
    board = None
    adafruit_dht = None

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
    
    @property
    def temperature(self) -> float:
        # Return slightly varying mock temperature
        return self._base_temp + random.uniform(-2.0, 2.0)
    
    @property
    def humidity(self) -> float:
        # Return slightly varying mock humidity
        return self._base_humidity + random.uniform(-5.0, 5.0)


def _initialize_dht11() -> Optional[Any]:
    if not _HAVE_HARDWARE:
        logger.info("Using mock DHT11 sensor")
        return _MockDHT11()
    
    try:
        dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)
        return dht_device
    except Exception as exc:
        logger.exception("Failed to initialize DHT11: %s", exc)
        return None


def read_dht11(dht_device: Any) -> Optional[DHTReading]:
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if temperature is None or humidity is None:
            return None
        return DHTReading(float(temperature), float(humidity))
    except RuntimeError as e:
        logger.warning("DHT11 read error: %s", e)
        return None
    except Exception as exc:
        logger.exception("Unexpected error reading DHT11: %s", exc)
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
