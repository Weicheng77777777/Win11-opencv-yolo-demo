"""Logging utility — writes to both console and file."""

import logging
import os
from datetime import datetime


def setup_logger(output_dir="outputs"):
    """Create a logger that prints to console and writes to a timestamped file."""
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(log_dir, f"run_{timestamp}.log")

    logger = logging.getLogger("gripper_demo")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S"))
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S"))
    logger.addHandler(ch)

    logger.info(f"SYSTEM_START log={log_path}")
    return logger
