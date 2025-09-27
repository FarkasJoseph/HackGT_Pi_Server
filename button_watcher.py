from gpiozero import Button
import time
import threading

class ButtonWatcher:
    def __init__(self, pin=26):
        self.button = Button(pin)
        self._pressed_event = threading.Event()
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._watch, daemon=True)

    def _watch(self):
        while not self._stop_event.is_set():
            if self.button.is_pressed:
                self._pressed_event.set()
                # Debounce: wait until released
                while self.button.is_pressed and not self._stop_event.is_set():
                    time.sleep(0.05)
            time.sleep(0.05)

    def start(self):
        self.thread.start()

    def wait_for_press(self, timeout=None):
        pressed = self._pressed_event.wait(timeout)
        if pressed:
            self._pressed_event.clear()
        return pressed

    def stop(self):
        self._stop_event.set()
        self.thread.join()

if __name__ == "__main__":
    watcher = ButtonWatcher(pin=26)
    watcher.start()
    print("Waiting for button press on GPIO 26...")
    try:
        while True:
            if watcher.wait_for_press():
                print("Button pressed!")
    except KeyboardInterrupt:
        watcher.stop()
        print("Exiting.")
