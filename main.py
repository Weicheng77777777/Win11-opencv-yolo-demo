"""
Camera + YOLO + Serial Gripper Demo
Detects objects with YOLO and controls a gripper via serial port.
"""

import cv2
import serial
import time
from ultralytics import YOLO

# ===== Config =====
CAMERA_ID = 0
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600
CONFIDENCE = 0.5
DEVICE = "cuda"  # "cuda" or "cpu"
MODEL = "yolo11n.pt"
GRIPPER_CLOSE = b"1"
GRIPPER_OPEN = b"0"
HOLD_SEC = 2.0       # hold gripper closed after last detection
COOLDOWN_SEC = 1.0   # min interval between triggers

# COCO classes commonly treated as waste
TRASH_CLASSES = {39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 54, 55, 67, 73}
# ==================

def main():
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {CAMERA_ID}")
        return

    print("Loading YOLO model...")
    model = YOLO(MODEL).to(DEVICE)
    names = model.names

    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
        print(f"Serial {SERIAL_PORT} opened")
    except serial.SerialException as e:
        print(f"Serial unavailable ({e}) — running visual-only")

    print("Press Q to quit | G toggle auto-grip")
    auto = True
    gripping = False
    last_cmd = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)[0]
        now = time.time()
        found = False

        for box in results.boxes:
            cid = int(box.cls[0])
            conf = float(box.conf[0])
            if cid not in TRASH_CLASSES or conf < CONFIDENCE:
                continue
            found = True
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{names[cid]} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Auto gripper
        if auto and ser and ser.is_open:
            if found and not gripping and (now - last_cmd) > COOLDOWN_SEC:
                ser.write(GRIPPER_CLOSE)
                print(f"[GRIP] CLOSE  t={now:.1f}")
                gripping = True
                last_cmd = now
            elif not found and gripping and (now - last_cmd) > HOLD_SEC:
                ser.write(GRIPPER_OPEN)
                print(f"[GRIP] OPEN   t={now:.1f}")
                gripping = False
                last_cmd = now

        mode = "AUTO" if auto else "MAN"
        grip = "HOLD" if gripping else "OPEN"
        cv2.putText(frame, f"{mode} | {grip}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Trash Gripper Demo", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("g"):
            auto = not auto
            print(f"Auto: {'ON' if auto else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()
    if ser and ser.is_open:
        ser.close()

if __name__ == "__main__":
    main()
