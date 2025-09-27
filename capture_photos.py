
import cv2
import time
import os
import glob

def run_photo_capture(output_dir="photos", max_photos=15, interval=1):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Output directory is '{output_dir}'.")

    # Clear the photos directory on function start
    existing_photos = glob.glob(os.path.join(output_dir, "photo_*.jpg"))
    for photo in existing_photos:
        try:
            os.remove(photo)
            print(f"[INFO] Deleted existing photo '{photo}' on startup.")
        except Exception as e:
            print(f"[ERROR] Could not delete '{photo}' on startup: {e}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return
    else:
        print("[INFO] Webcam stream opened successfully.")

    counter = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame from webcam.")
                break

            photo_filename = os.path.join(output_dir, f"photo_{counter:04d}.jpg")
            cv2.imwrite(photo_filename, frame)
            print(f"[INFO] Saved new photo as '{photo_filename}'.")

            # Delete oldest photo if more than max_photos exist
            photos = sorted(glob.glob(os.path.join(output_dir, "photo_*.jpg")))
            if len(photos) > max_photos:
                oldest = photos[0]
                try:
                    os.remove(oldest)
                    print(f"[INFO] Deleted oldest photo '{oldest}'.")
                except Exception as e:
                    print(f"[ERROR] Failed to delete '{oldest}': {e}")

            print(f"[STATUS] Total photos: {len(glob.glob(os.path.join(output_dir, 'photo_*.jpg')))}\n")
            counter += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        print("[INFO] Exiting on user interrupt.")

    finally:
        cap.release()
        print("[INFO] Webcam stream released.")

if __name__ == "__main__":
    run_photo_capture()
