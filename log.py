import sys
import time
from machine import RTC

rtc = RTC()

def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


def now():
    """
    ( year,month,day,weekday,hour,minute,second,microsecond )
    """
    return rtc.datetime()

def nowInString():
    n = now()
    return "%04d-%02d-%02d %02d:%02d:%02d.%06d" % (n[0], n[1], n[2], n[4], n[5], n[6], n[7])

def print_log(level, message):
    t = time.time()
    if int(t) < 696432783:
        t = str(t)
    else:
        t = nowInString()

    eprint("[%s][%s] %s" % (t, level, str(message)))

def trace(message):
    print_log("Trace", message)

def debug(message):
    print_log("Debug", message)

def info(message):
    print_log("Info", message)

def warn(message):
    print_log("Warn", message)

def error(message):
    print_log("Error", message)

def severe(message):
    print_log("Severe", message)

if __name__ == "__main__":
    info("test")