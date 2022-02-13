import sys
import time
from machine import RTC
from config import syslogconfig

rtc = RTC()

if syslogconfig.SYSLOG_ENABLE:
    from lib import usyslog

syslog: usyslog.UDPClient = None

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

def enableSyslog():
    if syslogconfig.SYSLOG_ENABLE:
        global syslog
        syslog = usyslog.UDPClient(ip=syslogconfig.SYSLOG_HOST, port=syslogconfig.SYSLOG_PORT)
        debug("Syslog enabled")

def print_log(level, message):
    t = time.time()
    if int(t) < 696432783:
        t = str(t)
    else:
        t = nowInString()

    eprint("[%s][%s] %s" % (t, level, str(message)))

def trace(message):
    if syslog is not None:
        syslog.debug(message)
    print_log("Trace", message)

def debug(message):
    if syslog is not None:
        syslog.debug(message)
    print_log("Debug", message)

def info(message):
    if syslog is not None:
        syslog.info(message)
    print_log("Info", message)

def warn(message):
    if syslog is not None:
        syslog.warning(message)
    print_log("Warn", message)

def error(message):
    if syslog is not None:
        syslog.error(message)
    print_log("Error", message)

def severe(message):
    if syslog is not None:
        syslog.critical(message)
    print_log("Severe", message)

if __name__ == "__main__":
    info("test")