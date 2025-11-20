import time
import board
import adafruit_dht
from typing import Any, Optional, NamedTuple
import logging

logger = logging.getLogger(__name__)

_dht11: Optional[Any] = None


class DHTReading(NamedTuple):
    temperature: float
    humidity: float


def _initialize_dht11() -> Optional[Any]:
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
