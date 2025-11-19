import RPi.GPIO as GPIO
from time import sleep

LED_PIN = 18  # Użyj pinu GPIO, do którego podłączyłeś anodę

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    print("Test diody LED - naciśnij CTRL+C, aby zakończyć.")
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Włącz LED
        print("LED WŁ.")
        sleep(0.5)

        GPIO.output(LED_PIN, GPIO.LOW)   # Wyłącz LED
        print("LED WYŁ.")
        sleep(0.5)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()