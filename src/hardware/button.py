from gpiozero import Button
from signal import pause

button = Button(27, pull_up=True, bounce_time=0.05)
button.when_pressed = lambda: print("Guziczek wcisniety")

pause()