import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

class RollingAudioCapture:
    def __init__(self, duration=15, refresh=1, output_file="last_15_seconds.wav", samplerate=44100, channels=1):
        self.duration = duration
        self.refresh = refresh
        self.output_file = output_file
        self.samplerate = samplerate
        self.channels = channels
        self.buffer_samples = duration * samplerate
        self.audio_buffer = np.zeros((self.buffer_samples, channels), dtype='float32')
        self.write_ptr = 0
        self.buffer_filled = False
        self.buffer_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._save_thread = threading.Thread(target=self._save_audio_loop, daemon=True)

    def audio_callback(self, indata, frames, time_info, status):
        with self.buffer_lock:
            end_ptr = self.write_ptr + frames
            if end_ptr < self.buffer_samples:
                self.audio_buffer[self.write_ptr:end_ptr] = indata
            else:
                first_part = self.buffer_samples - self.write_ptr
                self.audio_buffer[self.write_ptr:] = indata[:first_part]
                self.audio_buffer[:frames - first_part] = indata[first_part:]
                self.buffer_filled = True
            self.write_ptr = (self.write_ptr + frames) % self.buffer_samples
            if self.write_ptr == 0:
                self.buffer_filled = True

    def _save_audio_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.refresh)
            with self.buffer_lock:
                if self.buffer_filled:
                    end_ptr = self.write_ptr
                    if end_ptr > 0:
                        recent = np.vstack((self.audio_buffer[end_ptr:], self.audio_buffer[:end_ptr]))
                    else:
                        recent = self.audio_buffer.copy()
                    sf.write(self.output_file, recent, self.samplerate)
                    print(f"[{time.strftime('%H:%M:%S')}] Updated {self.output_file} with the last {self.duration} seconds of audio.")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Buffer not yet full: waiting to save output.")

    def start(self):
        self._save_thread.start()
        self._stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self.audio_callback, blocksize=1024)
        self._stream.start()
        print(f"Recording... Outputting rolling {self.duration}-second audio to {self.output_file}. Press Ctrl+C to stop.")

    def stop(self):
        self._stop_event.set()
        self._save_thread.join()
        self._stream.stop()
        self._stream.close()

    def get_buffer_lock(self):
        return self.buffer_lock

def run_rolling_audio_capture(duration=15, refresh=1, output_file="last_15_seconds.wav", samplerate=44100, channels=1):
    rac = RollingAudioCapture(duration, refresh, output_file, samplerate, channels)
    rac.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        rac.stop()
        print("Stopped recording.")

if __name__ == "__main__":
    run_rolling_audio_capture()
