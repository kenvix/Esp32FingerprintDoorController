import gpios
import log
import as608
from machine import Pin, Timer
import _thread

_isFingerDetecting = False
_isFingerDetectionShouldStop = False

def addFinger():
    log.info("Adding finger")
    as608.enroll_finger_to_device(gpios.fingerSession, as608)


def onFingerDetected(finger_id: int, confidence: float):
    log.info("Opening door")
    gpios.doorOpenAndClose()


def _doorFingerWakIrqHandler(pin: Pin):
    global _isFingerDetectionShouldStop, _isFingerDetecting
    if pin.value() == 1:
        if _isFingerDetecting is False:
            _thread.start_new_thread(_doorFingerWakIrqPressHandler, ())
    else:
        _doorFingerWakIrqReleaseHandler()


def _doorFingerWakIrqPressHandler():
    global _isFingerDetecting, _isFingerDetectionShouldStop
    _isFingerDetecting = True
    _isFingerDetectionShouldStop = False
    log.debug("Finger wak pin pressed")
    
    while not _isFingerDetectionShouldStop:
        if as608.search_fingerprint_on_device(gpios.fingerSession, as608, exit_if_no_finger=True):
            log.info("Finger checked: Finger id: %d | Confidence: %f" % (gpios.fingerSession.finger_id, gpios.fingerSession.confidence))
            onFingerDetected(gpios.fingerSession.finger_id, gpios.fingerSession.confidence)
            break
    
    _isFingerDetecting = False


def _doorFingerWakIrqReleaseHandler():
    global _isFingerDetectionShouldStop
    _isFingerDetectionShouldStop = True
    log.debug("Finger wak pin released ")


def startDoorController():
    log.info("Starting door controller")
    global _isFingerDetecting
    gpios.fingerWakPin.irq(
        trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
        handler=_doorFingerWakIrqHandler,
    )