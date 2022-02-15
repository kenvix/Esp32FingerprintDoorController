from config import gpioconfig
import gpios
import log
import as608
import sys
from machine import Pin, Timer
import _thread
from config import functionconfig
from messager import messager
import gc

isFingerDetecting = False
isFingerDetectionShouldStop = False
isFingerAdding = False
humanAlertTimer: Timer
fingerCheckTimer: Timer
fingerLastInsertedTime = None

def _addFingerOnNext():
    log.info("Finger: Put finger again.")
    gpios.beepBoth(time=400, num=2)

def addFinger():
    global isFingerAdding, fingerLastInsertedTime
    if isFingerAdding:
        return
    isFingerAdding = True
    try:
        log.info("Finger: Prepared to add finger, put your finger now.")
        gpios.beepBoth(time=200, num=4)
        gc.collect()
        as608.enroll_finger_to_device(gpios.fingerSession, as608, onNext=_addFingerOnNext)
        fingerLastInsertedTime = log.now()
        isFingerAdding = False
        log.info("Finger: Finger added. Location %d" % gpios.fingerSession.last_inserted_location)
        if functionconfig.FINGER_MESSAGE_ENABLE:
            messager.sendMessage(functionconfig.FINGER_MESSAGE_CONTENT % (log.nowInString(), log.nowInString(fingerLastInsertedTime), "添加指纹 %d" % gpios.fingerSession.last_inserted_location))
    except Exception as e:
        log.error("Finger: addFinger detector got a unexpected exception on: %s" % e)
        sys.print_exception(e)


def deleteFinger(location):
    gpios.fingerSession.delete_model(location)
    log.info("Finger: Deleted finger %d" % location)


def addFingerAsync():
    _thread.start_new_thread(addFinger, ())

def onFingerDetected(finger_id: int, confidence: float):
    gpios.beepBothOnce(1200)
    gpios.doorOpenAndClose()
    if functionconfig.DOOR_MESSAGE_ENABLE:
        messager.sendMessage(functionconfig.DOOR_MESSAGE_CONTENT % (log.nowInString(), "指纹", str(finger_id), "置信度 %f" % confidence))


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
    global isFingerDetecting, isFingerDetectionShouldStop, isFingerAdding
    isFingerDetecting = True
    isFingerDetectionShouldStop = False
    try:
        log.debug("Finger wak pin pressed")
        if isFingerAdding:
            log.debug("Finger adding, do not open door.")
            return
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
    except Exception as e:
        log.error("Finger: _doorFingerWakIrqPressHandler detector got a unexpected exception on: %s" % e)
        sys.print_exception(e)
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
        humanAlertTimer.init(period=150, mode=Timer.PERIODIC, callback=_humanSensorAlertTimerHandler)
    else:
        log.info("Human sensor released")
        gpios.pinBeepOutside.value(0)
        humanAlertTimer.deinit()


def _checkFingerSensor(timer=None):
    global isFingerDetecting, isFingerAdding
    if not isFingerDetecting and not isFingerAdding:
        try:
            if not gpios.fingerSession.check_module():
                log.warn("Finger sensor has errors, soft_reset")
                gpios.lightDoorAlertLed()
                gpios.fingerSession.soft_reset()
                gpios.unlightDoorAlertLed()
        except Exception as e:
            log.warn("Finger sensor down with error: %s" % e)
            fingerCheckTimer.deinit()
            gpios.lightDoorAlertLed()
            gpios.beepBoth(time=300, num=10)
            
            while True:
                try:
                    log.info("Finger sensor Reconnecting")
                    gpios.connectFinger()
                    break
                except Exception as ex:
                    gpios.beepBoth(time=300, num=10)
                    log.warn("Finger sensor reconnect failed with error: %s" % ex)

            gpios.unbeepBoth()
            gpios.unlightDoorAlertLed()
            fingerCheckTimer.init(period=gpioconfig.FINGET_KEEP_ALIVE_DELAY, mode=Timer.PERIODIC, callback=_checkFingerSensor)


def startFingerKeepAlive():
    global fingerCheckTimer
    log.info("Finger keepalive enabled")
    fingerCheckTimer = Timer(5)
    fingerCheckTimer.init(period=gpioconfig.FINGET_KEEP_ALIVE_DELAY, mode=Timer.PERIODIC, callback=_checkFingerSensor)


def startHumanSensor():
    global humanAlertTimer 
    if gpioconfig.HUMAN_SENSOR_ENABLE:
        log.info("Starting human sensor alterter")
        humanAlertTimer = Timer(4)
        if gpioconfig.HUMAN_SENSOR_ALERT_WHEN_DETECTED:
            gpios.pinHumanSensorIrqHandler = _pinHumanSensorIrqHandler