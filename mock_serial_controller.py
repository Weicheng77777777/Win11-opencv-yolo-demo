"""Mock serial controller for hardware-free development."""


class MockSerialController:
    """Simulates serial communication when no STM32 is connected."""

    def __init__(self, port=None, baud_rate=None, timeout=None):
        pass

    def send_command(self, command):
        print(f"[MockSerial] send: {command}")
        print("[MockSerial] recv: DONE")
        return "DONE"

    def open_gripper(self):
        return self.send_command("OPEN")

    def close_gripper(self):
        return self.send_command("CLOSE")

    def grab(self):
        return self.send_command("GRAB")

    def stop(self):
        return self.send_command("STOP")

    def close(self):
        print("[MockSerial] closed")
