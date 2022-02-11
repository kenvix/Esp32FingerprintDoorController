import time
from machine import UART
from config import gpioconfig

class Serial(UART):
    def __init__(self, port, baudrate=9600, bytesize=8, stopbits=1, timeout=1) -> None:
        if isinstance(port, str) and port.startswith("COM"):
            port = int(port[3:]) - 1
        super().__init__(port)
        self.init(baudrate, bits=bytesize, parity=None, stop=stopbits, timeout=timeout)

    def read(self, num=None):
        if num is None:
            r = super().read()
            if r is None:
                return b''
            else:
                return r
        else:
            currentNum = 0
            result = b''
            while currentNum < num:
                r = super().read(num - currentNum)
                if r is None or len(r) == 0:
                    time.sleep(gpioconfig.IO_BLOCK_SLEEP_TIME)
                else:
                    currentNum += len(r)
                    result += r

            return result

    def close(self):
        self.deinit()