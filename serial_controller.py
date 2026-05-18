"""Real serial controller for STM32 communication."""

import serial


class SerialController:
    """Sends OPEN/CLOSE/GRAB/STOP commands via serial port."""

    def __init__(self, port="COM3", baud_rate=115200, timeout=1):
        self.ser = serial.Serial(port, baud_rate, timeout=timeout)

    def send_command(self, command):
        """Send a string command with newline and return response."""
        msg = command.strip() + "\n"
        self.ser.write(msg.encode("utf-8"))
        response = self.ser.readline().decode("utf-8", errors="ignore").strip()
        return response

    def open_gripper(self):
        return self.send_command("OPEN")

    def close_gripper(self):
        return self.send_command("CLOSE")

    def grab(self):
        return self.send_command("GRAB")

    def stop(self):
        return self.send_command("STOP")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
