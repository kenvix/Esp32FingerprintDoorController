import gpios
import log
import as608
from machine import Pin, Timer
import _thread

_isFingerDetecting = False

def addFinger():
    log.info("Adding finger")
    as608.enroll_finger_to_device(gpios.fingerSession, as608)


def _doorFingerWakIrqHandler(pin: Pin):
    if pin.value() == 1:
        if _isFingerDetecting is False:
            _thread.start_new_thread(_doorFingerWakIrqPressHandler, ())
    else:
        _doorFingerWakIrqReleaseHandler()


def _doorFingerWakIrqPressHandler():
    global _isFingerDetecting
    _isFingerDetecting = True
    log.debug("Finger wak pin pressed")
    
    while _isFingerDetecting:
        if as608.search_fingerprint_on_device(gpios.fingerSession, as608, exit_if_no_finger=True):
            log.info("Finger check pass. Opening door")
            gpios.doorOpenAndClose()
            return


def _doorFingerWakIrqReleaseHandler():
    global _isFingerDetecting
    _isFingerDetecting = False
    log.debug("Finger wak pin released ")


def startDoorController():
    log.info("Starting door controller")
    global _isFingerDetecting
    gpios.fingerWakPin.irq(
        trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
        handler=_doorFingerWakIrqHandler,
    )