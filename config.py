"""Centralized configuration for trash gripper demo."""

# Camera
CAMERA_ID = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# YOLO
MODEL_PATH = "yolo11n.pt"
DEVICE = "cuda"  # "cuda" or "cpu"
IMG_SIZE = 640
CONF_THRESHOLD = 0.5

TARGET_CLASSES = ["bottle", "cup", "banana", "apple", "orange"]

# Logic
STABLE_FRAME_COUNT = 3
HOLD_SEC = 2.0
COOLDOWN_SEC = 5.0
AUTO_MODE_DEFAULT = True

# Serial
USE_MOCK_SERIAL = True
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1

# Output
SAVE_VIDEO = False
SAVE_SCREENSHOT = True
OUTPUT_DIR = "outputs"
