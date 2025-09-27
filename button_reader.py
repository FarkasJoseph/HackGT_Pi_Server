from gpiozero import Button
import time

# GPIO 26 is BCM pin 26 (physical pin 37)
button = Button(26)

print("Waiting for button press on GPIO 26...")

try:
    while True:
        if button.is_pressed:
            print("Button pressed!")
            # Debounce: wait until released
            while button.is_pressed:
                time.sleep(0.05)
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Exiting.")
