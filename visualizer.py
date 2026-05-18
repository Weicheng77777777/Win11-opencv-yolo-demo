"""Visualization helpers for drawing on frames."""

import cv2


def draw_detections(frame, detections):
    """Draw bounding boxes, labels, and center points."""
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = f"{det['class_name']} {det['confidence']:.2f}"
        cx, cy = det["center"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)


def draw_status_panel(frame, info):
    """Draw status overlay in top-left corner.

    info dict: state, auto, serial, target, action, fps
    """
    lines = [
        f"STATE: {info.get('state', 'N/A')}",
        f"AUTO: {'ON' if info.get('auto') else 'OFF'}",
        f"SERIAL: {info.get('serial', 'N/A')}",
        f"TARGET: {info.get('target', 'NONE')}",
        f"ACTION: {info.get('action', 'NONE')}",
        f"FPS: {info.get('fps', 0)}",
    ]
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (10, 30 + i * 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
