# HackGT_Pi_Server

Lightweight Raspberry Pi server for capturing rolling audio and continuous photos, packaging recent captures, and uploading to a remote endpoint when a physical button is pressed.

## Features

- Continuous photo capture using OpenCV (webcam) with configurable max photos and interval.
- Rolling audio capture that maintains the last N seconds of audio in a buffer and periodically writes to disk.
- Button watcher using gpiozero to trigger packaging of recent photos and audio into a .tar.gz and upload via HTTP multipart/form-data.
- Simple packaging and upload logic with progress printing.

## Repository structure

- `server_runner.py` - Orchestrator: starts photo and audio capture, watches the physical button, packages outputs, and uploads them.
- `capture_photos.py` - Continuous webcam capture. Functions: `run_photo_capture(...)` and `trigger_photo_capture(...)`.
- `rolling_audio_capture.py` - `RollingAudioCapture` class for continuous rolling audio capture and periodic writes.
- `button_watcher.py` - `ButtonWatcher` class to watch a GPIO pin for button presses.
- `button_reader.py` - Simple standalone script to read button presses from GPIO 26 (useful for testing hardware).
- `requirements.txt` - Python package dependencies.

## Hardware

- A Raspberry Pi (or Linux device with GPIO) is expected.
- A webcam compatible with OpenCV (V4L2) plugged into the Pi.
- A physical button connected to GPIO 26 (BCM numbering). Adjust pin numbers in code if needed.

## Setup

1. Create a Python 3 virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) If running on Raspberry Pi OS and using system audio input, ensure `alsa`/`pulseaudio` and appropriate drivers are configured. `sounddevice` may require `portaudio` to be installed via system package manager.

## Configuration

- Edit `server_runner.py` to change the upload `endpoint` in `upload_tar_gz()` to your server's URL.
- Adjust `photo_buffer` and `audio_buffer` constants in `server_runner.py` to control how many photos and how many seconds of audio are packaged.
- GPIO pin defaults to 26 (BCM) in `button_watcher.py` and `button_reader.py`.

## Running

- To run the full orchestrator (photo + audio capture, button-triggered packaging + upload):

```bash
python server_runner.py
```

- To run components individually for testing:

```bash
python capture_photos.py
python rolling_audio_capture.py
python button_reader.py
python button_watcher.py
```

## Notes & Troubleshooting

- Webcam errors: If OpenCV cannot open the webcam, verify `ls /dev/video*` and ensure the camera is available. You may need to adjust the device index in `cv2.VideoCapture(0)`.
- Audio errors: `sounddevice` requires PortAudio. On Raspberry Pi:

```bash
sudo apt install libportaudio2 libportaudio-dev
pip install sounddevice
```

- GPIO: Run scripts as a user with GPIO access (`gpiozero` usually works with default pi user). If permissions errors occur, consult RPi OS docs or add your user to the `gpio` group.

## License

This repository is provided as-is. Add a license file if needed.

## Next steps / Improvements

- Add a small configuration file or CLI args for endpoints, buffer sizes, and GPIO pins.
- Add unit tests and CI checks for packaging and upload logic (mocking hardware and network).
- Implement retries and backoff for uploads.
