import serial
import time

class CAT:
    def __init__(self, port, baud=4800, timeout=1):
        self.ser = serial.Serial(port, baud, timeout=timeout)

    def send(self, cmd: str) -> str:
        if not cmd.endswith(";"):
            cmd += ";"
        self.ser.write(cmd.encode("ascii"))
        time.sleep(0.05)
        return self.ser.read_until(b";").decode("ascii")

    def close(self):
        self.ser.close()
