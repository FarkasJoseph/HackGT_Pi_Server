
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

buffer_lock_global = threading.Lock()

def run_rolling_audio_capture(duration=15, refresh=1, output_file="last_15_seconds.wav", samplerate=44100, channels=1):
    buffer_samples = duration * samplerate
    audio_buffer = np.zeros((buffer_samples, channels), dtype='float32')
    write_ptr = [0]  # Use list for mutability in nested functions
    buffer_filled = [False]
    global buffer_lock_global
    buffer_lock = buffer_lock_global

    def audio_callback(indata, frames, time_info, status):
        with buffer_lock:
            end_ptr = write_ptr[0] + frames
            if end_ptr < buffer_samples:
                audio_buffer[write_ptr[0]:end_ptr] = indata
            else:
                first_part = buffer_samples - write_ptr[0]
                audio_buffer[write_ptr[0]:] = indata[:first_part]
                audio_buffer[:frames - first_part] = indata[first_part:]
                buffer_filled[0] = True
            write_ptr[0] = (write_ptr[0] + frames) % buffer_samples
            if write_ptr[0] == 0:
                buffer_filled[0] = True

    def save_audio_loop():
        while True:
            time.sleep(refresh)
            with buffer_lock:
                if buffer_filled[0]:
                    end_ptr = write_ptr[0]
                    if end_ptr > 0:
                        recent = np.vstack((audio_buffer[end_ptr:], audio_buffer[:end_ptr]))
                    else:
                        recent = audio_buffer.copy()
                    sf.write(output_file, recent, samplerate)
                    print(f"[{time.strftime('%H:%M:%S')}] Updated {output_file} with the last {duration} seconds of audio.")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Buffer not yet full: waiting to save output.")

    threading.Thread(target=save_audio_loop, daemon=True).start()

def get_audio_buffer_lock():
    return buffer_lock_global
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback, blocksize=1024):
        print(f"Recording... Outputting rolling {duration}-second audio to {output_file}. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped recording.")

if __name__ == "__main__":
    run_rolling_audio_capture()
