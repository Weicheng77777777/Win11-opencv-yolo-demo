"""Main entry — wires camera, detector, state machine, and gripper."""

import time
import os
import cv2

import config
from detector import Detector
from state_machine import StateMachine
from visualizer import draw_detections, draw_status_panel
from logger_utils import setup_logger

# Serial: pick real or mock
if config.USE_MOCK_SERIAL:
    from mock_serial_controller import MockSerialController as Gripper
else:
    from serial_controller import SerialController as Gripper


def main():
    logger = setup_logger(config.OUTPUT_DIR)

    # Camera
    cap = cv2.VideoCapture(config.CAMERA_ID)
    if not cap.isOpened():
        logger.error(f"CAMERA camera {config.CAMERA_ID} open failed")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    # Detector
    logger.info(f"MODEL loading {config.MODEL_PATH} device={config.DEVICE}")
    detector = Detector(
        model_path=config.MODEL_PATH,
        target_classes=config.TARGET_CLASSES,
        conf_threshold=config.CONF_THRESHOLD,
        img_size=config.IMG_SIZE,
        device=config.DEVICE,
    )
    logger.info(f"MODEL ready targets={config.TARGET_CLASSES}")

    # Gripper
    try:
        gripper = Gripper(
            port=config.SERIAL_PORT,
            baud_rate=config.BAUD_RATE,
            timeout=config.SERIAL_TIMEOUT,
        )
        logger.info(f"SERIAL {'MOCK' if config.USE_MOCK_SERIAL else config.SERIAL_PORT}")
    except Exception as e:
        logger.error(f"SERIAL init failed: {e}")
        return

    # State machine
    sm = StateMachine(
        stable_frame_count=config.STABLE_FRAME_COUNT,
        hold_sec=config.HOLD_SEC,
        cooldown_sec=config.COOLDOWN_SEC,
    )
    sm.auto = config.AUTO_MODE_DEFAULT

    logger.info("KEYS: Q=quit G=auto R=reset O=open SPACE=grab S=screenshot")

    serial_label = "MOCK" if config.USE_MOCK_SERIAL else "REAL"
    last_action = "NONE"
    fps = 0
    frame_count = 0
    fps_timer = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("CAMERA read failed")
            break

        now = time.time()

        # Detect
        detections = detector.detect(frame)
        target_found = len(detections) > 0
        best = max(detections, key=lambda d: d["confidence"]) if detections else None

        # State machine
        action, old_state, new_state = sm.update(target_found, now)
        if old_state != new_state:
            logger.info(f"STATE {old_state} -> {new_state}")
        if action == "GRAB":
            gripper.grab()
            last_action = "GRAB"
            logger.info("COMMAND GRAB")
        elif action == "OPEN":
            gripper.open_gripper()
            last_action = "OPEN"
            logger.info("COMMAND OPEN")

        # Update action display
        if sm.state in ("GRAB", "HOLD"):
            last_action = "GRAB"
        elif sm.state == "RELEASE":
            last_action = "OPEN"
        elif sm.state in ("WAIT", "FOUND", "COOLDOWN"):
            last_action = "NONE"

        # Draw
        draw_detections(frame, detections)
        draw_status_panel(frame, {
            "state": sm.state,
            "auto": sm.auto,
            "serial": serial_label,
            "target": f"{best['class_name']} {best['confidence']:.2f}" if best else "NONE",
            "action": last_action,
            "fps": fps,
        })

        # FPS
        frame_count += 1
        if now - fps_timer >= 1.0:
            fps = frame_count
            frame_count = 0
            fps_timer = now

        # Show
        cv2.imshow("Trash Gripper Demo", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            logger.info("KEY quit")
            break
        elif key == ord("g"):
            sm.auto = not sm.auto
            logger.info(f"KEY auto={'ON' if sm.auto else 'OFF'}")
        elif key == ord("r"):
            sm.reset()
            last_action = "NONE"
            logger.info("KEY reset")
        elif key == ord("o"):
            gripper.open_gripper()
            last_action = "OPEN"
            logger.info("KEY manual OPEN")
        elif key == ord(" "):
            gripper.grab()
            last_action = "GRAB"
            logger.info("KEY manual GRAB")
        elif key == ord("s"):
            shot_dir = os.path.join(config.OUTPUT_DIR, "screenshots")
            os.makedirs(shot_dir, exist_ok=True)
            path = os.path.join(shot_dir, f"screenshot_{int(now)}.jpg")
            cv2.imwrite(path, frame)
            logger.info(f"KEY screenshot saved {path}")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    gripper.close()
    logger.info("SYSTEM_EXIT")


if __name__ == "__main__":
    main()
