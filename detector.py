"""YOLO detection module."""

from ultralytics import YOLO


class Detector:
    """Wraps YOLO model for target detection."""

    def __init__(self, model_path="yolo11n.pt", target_classes=None,
                 conf_threshold=0.5, img_size=640, device="cuda"):
        self.model = YOLO(model_path).to(device)
        self.names = self.model.names
        self.img_size = img_size
        self.conf_threshold = conf_threshold

        # Convert target class names to IDs once
        target_classes = target_classes or []
        self.target_ids = [
            cid for cid, name in self.names.items()
            if name in target_classes
        ]

    def detect(self, frame):
        """Run YOLO on a frame and return filtered detections.

        Each detection: {class_name, confidence, box: [x1,y1,x2,y2], center: [cx,cy]}
        """
        results = self.model(frame, imgsz=self.img_size,
                             conf=self.conf_threshold, verbose=False)[0]

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in self.target_ids:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({
                "class_name": self.names[cls_id],
                "confidence": float(box.conf[0]),
                "box": [x1, y1, x2, y2],
                "center": [(x1 + x2) // 2, (y1 + y2) // 2],
            })

        return detections
