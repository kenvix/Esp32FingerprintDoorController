import gpios
import log
import as608
from machine import Pin, Timer
import _thread

isFingerDetecting = False
isFingerDetectionShouldStop = False
isFingerAdding = False

def addFinger():
    global isFingerAdding
    isFingerAdding = True
    log.info("Adding finger")
    gpios.beepOutside(time=150, num=4)
    as608.enroll_finger_to_device(gpios.fingerSession, as608)
    isFingerAdding = False

def addFingerAsync():
    _thread.start_new_thread(addFinger, ())

def onFingerDetected(finger_id: int, confidence: float):
    log.info("Opening door")
    gpios.beepOutsideOnce(1000)
    gpios.doorOpenAndClose()


def _doorFingerWakIrqHandler(pin: Pin):
    global isFingerDetectionShouldStop, isFingerDetecting, isFingerAdding
    if isFingerAdding:
        return

    if pin.value() == 1:
        if isFingerDetecting is False:
            _thread.start_new_thread(_doorFingerWakIrqPressHandler, ())
    else:
        _doorFingerWakIrqReleaseHandler()


def _doorFingerWakIrqPressHandler():
    global isFingerDetecting, isFingerDetectionShouldStop
    isFingerDetecting = True
    isFingerDetectionShouldStop = False
    log.debug("Finger wak pin pressed")
    
    while not isFingerDetectionShouldStop:
        if as608.search_fingerprint_on_device(gpios.fingerSession, as608, exit_if_no_finger=True):
            log.info("Finger checked: Finger id: %d | Confidence: %f" % (gpios.fingerSession.finger_id, gpios.fingerSession.confidence))
            onFingerDetected(gpios.fingerSession.finger_id, gpios.fingerSession.confidence)
            break
        else:
            log.info("Finger not found or unmatched")
            gpios.beepOutside(time=200, num=2)
    
    isFingerDetecting = False


def _doorFingerWakIrqReleaseHandler():
    global isFingerDetectionShouldStop
    isFingerDetectionShouldStop = True
    log.debug("Finger wak pin released ")


def startDoorController():
    log.info("Starting door controller")
    global isFingerDetecting
    gpios.fingerWakPin.irq(
        trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
        handler=_doorFingerWakIrqHandler,
    )