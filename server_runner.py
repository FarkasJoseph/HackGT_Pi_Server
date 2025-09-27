
import time
import tarfile
import os
import glob
import threading
from capture_photos import run_photo_capture, trigger_photo_capture
from rolling_audio_capture import run_rolling_audio_capture

photo_buffer = 15
audio_buffer = 15

def package_outputs(photo_dir="photos", audio_file="audio_buffer.wav", archive_name="output_package.gz"):
    # Collect latest photo files
    photos = sorted(glob.glob(os.path.join(photo_dir, "photo_*.jpg")))
    files_to_package = photos[-photo_buffer:] if len(photos) >= photo_buffer else photos  # Package last 15 photos
    temp_audio_file = None
    if os.path.exists(audio_file):
        # Make a temporary copy of the WAV file
        temp_audio_file = audio_file + ".copy.wav"
        import shutil
        shutil.copy2(audio_file, temp_audio_file)
        files_to_package.append(temp_audio_file)
    else:
        print(f"[WARN] Audio file '{audio_file}' not found for packaging.")
    # Create a .tar.gz archive
    archive_name = archive_name if archive_name.endswith('.tar.gz') else archive_name.replace('.gz', '.tar.gz')
    with tarfile.open(archive_name, "w:gz") as tar:
        for fname in files_to_package:
            tar.add(fname, arcname=os.path.basename(fname))
            print(f"[INFO] Added '{fname}' to archive '{archive_name}'.")
    print(f"[INFO] Packaged {len(files_to_package)} files into '{archive_name}'.")
    # Delete the temporary audio copy
    if temp_audio_file and os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)

def start_services_and_package():
    # Start photo and audio capture in background threads
    photo_thread = threading.Thread(target=run_photo_capture, kwargs={"output_dir": "photos", "max_photos": photo_buffer, "interval": 1}, daemon=True)
    audio_thread = threading.Thread(target=run_rolling_audio_capture, kwargs={"duration": audio_buffer, "refresh": 1, "output_file": "audio_buffer.wav", "samplerate": 44100, "channels": 1}, daemon=True)
    photo_thread.start()
    audio_thread.start()
    print("[INFO] Photo and audio capture started.")
    print("[INFO] Press Enter to package outputs, or Ctrl+C to exit.")
    try:
        while True:
            input()  # Wait for Enter key
            trigger_photo_capture(output_dir="photos", max_photos=photo_buffer)
            package_outputs()
    except KeyboardInterrupt:
        print("[INFO] Server runner exiting.")

if __name__ == "__main__":
    start_services_and_package()
