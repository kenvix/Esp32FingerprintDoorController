import time
from machine import UART
from config import gpioconfig

class Serial(UART):
    def __init__(self, port, baudrate=9600, bytesize=8, stopbits=1, timeout=1) -> None:
        if isinstance(port, str) and port.startswith("COM"):
            port = int(port[3:]) - 1
        super().__init__(port)
        self.read_timeout = gpioconfig.IO_READ_TIMEOUT
        self.timeout_counter_init = self.read_timeout / gpioconfig.IO_BLOCK_SLEEP_TIME
        self.init(baudrate, bits=bytesize, parity=None, stop=stopbits, timeout=timeout)

    def set_read_timeout(self, timeout):
        self.read_timeout = timeout
        self.timeout_counter_init = self.read_timeout / gpioconfig.IO_BLOCK_SLEEP_TIME

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
            timeout_counter = self.timeout_counter_init

            while currentNum < num and timeout_counter >= 0:
                r = super().read(num - currentNum)
                if r is None or len(r) == 0:
                    time.sleep(gpioconfig.IO_BLOCK_SLEEP_TIME)
                    timeout_counter -= 1
                else:
                    currentNum += len(r)
                    result += r
                    timeout_counter = self.timeout_counter_init

            if result is None or len(result) == 0 and timeout_counter < 0:
                raise TimeoutError("UART Read time out.")

            return result

    def close(self):
        self.deinit()