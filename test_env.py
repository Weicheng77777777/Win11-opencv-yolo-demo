"""Quick check: camera + YOLO + serial environment."""
import ultralytics
import cv2
import serial

print(f"ultralytics  : {ultralytics.__version__}")
print(f"opencv-python: {cv2.__version__}")
print(f"pyserial     : {serial.__version__}")
print("Environment OK!")
