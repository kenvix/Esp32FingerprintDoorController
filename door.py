from config import gpioconfig
import gpios
import log
import as608
from machine import Pin, Timer
import _thread

isFingerDetecting = False
isFingerDetectionShouldStop = False
isFingerAdding = False
humanAlertTimer: Timer

def addFinger():
    global isFingerAdding
    isFingerAdding = True
    log.info("Finger: Prepared to add finger, put your finger now.")
    gpios.beepOutside(time=150, num=4)
    as608.enroll_finger_to_device(gpios.fingerSession, as608)
    isFingerAdding = False

def addFingerAsync():
    _thread.start_new_thread(addFinger, ())

def onFingerDetected(finger_id: int, confidence: float):
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
    gpios.lightDoorAlertLed()
    while not isFingerDetectionShouldStop:
        if as608.search_fingerprint_on_device(gpios.fingerSession, as608, exit_if_no_finger=True):
            log.info("Finger checked: Finger id: %d | Confidence: %f" % (gpios.fingerSession.finger_id, gpios.fingerSession.confidence))
            onFingerDetected(gpios.fingerSession.finger_id, gpios.fingerSession.confidence)
            break
        else:
            log.info("Finger not found or unmatched")
            gpios.beepOutside(time=200, num=2)
    
    gpios.unlightDoorAlertLed()
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

def _humanSensorAlertTimerHandler(timer):
    gpios.pinBeepOutside.value(not gpios.pinBeepOutside.value())

def _pinHumanSensorIrqHandler(pin: Pin):
    if pin.value() == 1:    
        log.info("Human sensor detected")
        gpios.pinBeepOutside.value(1)
        humanAlertTimer.init(period=200, mode=Timer.PERIODIC, callback=_humanSensorAlertTimerHandler)
    else:
        log.info("Human sensor released")
        gpios.pinBeepOutside.value(0)
        humanAlertTimer.deinit()

def startHumanSensor():
    global humanAlertTimer 
    if gpioconfig.HUMAN_SENSOR_ENABLE:
        log.info("Starting human sensor alterter")
        humanAlertTimer = Timer(-1)
        if gpioconfig.HUMAN_SENSOR_ALERT_WHEN_DETECTED:
            gpios.pinHumanSensorIrqHandler = _pinHumanSensorIrqHandler