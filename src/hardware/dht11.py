import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

while True:
    try:
        t = dht.temperature
        h = dht.humidity
        if t is not None and h is not None:
            print(f"Temp: {t:.1f}°C | Wilgotność: {h:.1f}%")
        else:
            print("Brak danych – próbuję ponownie...")
    except RuntimeError as e:
        print("Błąd odczytu:", e)
    time.sleep(2)