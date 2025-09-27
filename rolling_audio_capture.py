import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

DURATION = 15      # seconds to keep
REFRESH = 1        # output file update interval, seconds
OUTPUT_FILE = "last_15_seconds.wav"
SAMPLERATE = 44100 # samples per second
CHANNELS = 1       # mono

# Buffer for 15 seconds of audio
buffer_samples = DURATION * SAMPLERATE
audio_buffer = np.zeros((buffer_samples, CHANNELS), dtype='float32')
write_ptr = 0
buffer_filled = False
buffer_lock = threading.Lock()

def audio_callback(indata, frames, time_info, status):
    global write_ptr, buffer_filled
    with buffer_lock:
        end_ptr = write_ptr + frames
        if end_ptr < buffer_samples:
            audio_buffer[write_ptr:end_ptr] = indata
        else:
            first_part = buffer_samples - write_ptr
            audio_buffer[write_ptr:] = indata[:first_part]
            audio_buffer[:frames - first_part] = indata[first_part:]
            buffer_filled = True
        write_ptr = (write_ptr + frames) % buffer_samples
        if write_ptr == 0:
            buffer_filled = True

def save_audio_loop():
    while True:
        time.sleep(REFRESH)
        with buffer_lock:
            if buffer_filled:
                # Buffer is full: output last 15 seconds
                end_ptr = write_ptr
                start_ptr = (end_ptr + 1) % buffer_samples
                if end_ptr > 0:
                    recent = np.vstack((audio_buffer[end_ptr:], audio_buffer[:end_ptr]))
                else:
                    recent = audio_buffer.copy()
                sf.write(OUTPUT_FILE, recent, SAMPLERATE)
                print(f"[{time.strftime('%H:%M:%S')}] Updated {OUTPUT_FILE} with the last {DURATION} seconds of audio.")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Buffer not yet full: waiting to save output.")

def main():
    threading.Thread(target=save_audio_loop, daemon=True).start()
    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, callback=audio_callback, blocksize=1024):
        print(f"Recording... Outputting rolling {DURATION}-second audio to {OUTPUT_FILE}. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped recording.")

if __name__ == "__main__":
    main()
