import time
from typing import Any, Optional, NamedTuple
import logging
import random

logger = logging.getLogger(__name__)

# DHT11 Pin - GPIO 22 (physical pin 15)
# Avoid GPIO 4 as it can have conflicts with 1-wire interface
DHT_PIN = 22

# Try to import hardware libraries, fall back to mock
_HAVE_HARDWARE = False
try:
    import Adafruit_DHT
    _HAVE_HARDWARE = True
except (ImportError, NotImplementedError) as e:
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
    """Real DHT11 sensor wrapper using Adafruit_DHT library."""
    
    def __init__(self, pin: int):
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11
        logger.info("DHT11 sensor initialized on GPIO %d", pin)
    
    def read(self) -> Optional[DHTReading]:
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin, retries=5, delay_seconds=2)
        if humidity is not None and temperature is not None:
            return DHTReading(float(temperature), float(humidity))
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
