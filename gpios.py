from machine import Timer
from machine import Pin
import machine
from config import gpioconfig
import log
from machine import PWM

if gpioconfig.FINGER_ENABLE:
    import as608

tmd = None
pinStatus: Pin
timerStatus: PWM
pinBootButton: Pin
pinBeepInside: Pin
pinBeepOutside: Pin
pinBootButtonIrqHandler = lambda _: log.debug("Button Boot Pressed")
fingerSession: as608.Operation = None
fingerWakPin: Pin = None

isDoorOperating = False
isDoorForceLocked = False
isDoorForceLockButtonWaiting = False
pinFingerWakIrqHandler = lambda _: log.debug("Finger wak pin pressed")
pinMotor: Pin
pinDoorForceLock: Pin
pinDoorForceLockStatusLed: Pin = None
motorPwmTimer = Timer(1)
motorPwm: PWM
beepTimer = Timer(2)
doorForceLockButtonTimer: Timer
BEEP_INSIDE = 1
BEEP_OUSIDE = 2
pinWlanAlertLed: Pin = None
pinDoorAlertLed: Pin = None
pinHumanSensor: Pin
pinHumanSensorIrqHandler = lambda pin: log.debug("Hunman sensor changed to %d" % pin.value())

def loadPin():
    global pinStatus, pinBootButton, pinLight, pinBootButtonIrqHandler, fingerSession, fingerWakPin, timerStatus, pinMotor, pinBeepInside, pinBeepOutside, pinDoorForceLock, pinDoorForceLockStatusLed, pinWlanAlertLed, pinDoorAlertLed, doorForceLockButtonTimer, motorPwm, pinHumanSensor
    pinStatus: Pin = machine.Pin(gpioconfig.LED_STATUS_PIN, Pin.OUT)
    pinStatus.value(0)
    pinBootButton: Pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    pinBootButton.irq(
        trigger=Pin.IRQ_FALLING,
        handler=pinBootButtonIrqHandler
    )
    # timerStatus = None
    # timerStatus = Timer(-1)
    timerStatus = PWM(pinStatus, freq=1, duty=0)
    if gpioconfig.DOOR_MOTOR_ENABLE:
        pinMotor: Pin = machine.Pin(gpioconfig.DOOR_MOTOR_PIN, Pin.OUT)
        if gpioconfig.DOOR_MOTOR_KEEP_SIGNAL:
            motorPwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)
    if gpioconfig.BEEP_INSIDE_PIN > 0:
        pinBeepInside: Pin = machine.Pin(gpioconfig.BEEP_INSIDE_PIN, Pin.OUT)
        pinBeepInside.value(0)
    if gpioconfig.BEEP_OUTSIDE_PIN > 0:
        pinBeepOutside: Pin = machine.Pin(gpioconfig.BEEP_OUTSIDE_PIN, Pin.OUT)
        pinBeepOutside.value(0)
    if gpioconfig.DOOR_FORCE_LOCK_PIN > 0:
        pinDoorForceLock: Pin = machine.Pin(gpioconfig.DOOR_FORCE_LOCK_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        doorForceLockButtonTimer = Timer(-1)
        pinDoorForceLock.irq(
            trigger=Pin.IRQ_FALLING,
            handler=pinDoorForceLockButtonIrqHandler
        )
    if gpioconfig.DOOR_FORCE_LOCK_STATUS_LED_PIN > 0:
        pinDoorForceLockStatusLed: Pin = machine.Pin(gpioconfig.DOOR_FORCE_LOCK_STATUS_LED_PIN, Pin.OUT)
        pinDoorForceLockStatusLed.value(0)
    if gpioconfig.WLAN_ALERT_LED_PIN > 0:
        pinWlanAlertLed: Pin = machine.Pin(gpioconfig.WLAN_ALERT_LED_PIN, Pin.OUT)
        pinWlanAlertLed.value(0)
    if gpioconfig.DOOR_ALERT_LED_PIN > 0:
        pinDoorAlertLed: Pin = machine.Pin(gpioconfig.DOOR_ALERT_LED_PIN, Pin.OUT)
        pinDoorAlertLed.value(0)
    if gpioconfig.HUMAN_SENSOR_ENABLE:
        pinHumanSensor = machine.Pin(gpioconfig.HUMAN_SENSOR_PIN, machine.Pin.IN)
        pinHumanSensor.irq(
            trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
            handler=pinHumanSensorIrqHandler
        )

def lightWlanAlertLed():
    if pinWlanAlertLed is not None:
        pinWlanAlertLed.value(1)

def lightDoorAlertLed():
    if pinDoorAlertLed is not None:
        pinDoorAlertLed.value(1)

def unlightDoorAlertLed():
    if pinDoorAlertLed is not None:
        pinDoorAlertLed.value(0)

def unlightWlanAlertLed():
    if pinWlanAlertLed is not None:
        pinWlanAlertLed.value(0)

# def blinkStatusLED(freq = 3, duty = 20):
#     global timerStatus
#     if timerStatus is not None:
#         timerStatus.deinit()

#     timerStatus = PWM(pinStatus, freq=freq, duty=duty)
#     return timerStatus

def pinDoorForceLockButtonIrqHandler(pin):
    global isDoorForceLocked, isDoorForceLockButtonWaiting
    if isDoorForceLockButtonWaiting:
        return
    
    isDoorForceLockButtonWaiting = True
    doorForceLockButtonTimer.init(period=80, mode=Timer.ONE_SHOT, callback=_doorForceLockButtonTimeout)
    
def _doorForceLockButtonTimeout(timer):
    global isDoorForceLockButtonWaiting, isDoorForceLocked
    if pinDoorForceLock.value() == 0:
        isDoorForceLocked = not isDoorForceLocked
        if isDoorForceLocked:
            log.info("Door force locked")
            if pinDoorForceLockStatusLed is not None:
                pinDoorForceLockStatusLed.value(1)
        else:
            log.info("Door force unlocked")
            if pinDoorForceLockStatusLed is not None:
                pinDoorForceLockStatusLed.value(0)

    isDoorForceLockButtonWaiting = False

def blinkStatusLED(period=350):
    global timerStatus
    timerStatus.duty(512)
    timerStatus.freq(int(1 / period * 1000))


def cancelBlinkStatusLED():
    global timerStatus
    timerStatus.duty(0)
    pinStatus.value(0)

def beepOutsideOnce(time=300):
    pinBeepOutside.value(1)
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: pinBeepOutside.value(0))

def beepInsideOnce(time=300):
    pinBeepInside.value(1)
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: pinBeepInside.value(0))

def unbeepBoth(*args, **kwargs):
    beepTimer.deinit()
    pinBeepOutside.value(0)
    pinBeepInside.value(0)

def beepBothOnce(time=300):
    pinBeepInside.value(1)
    pinBeepOutside.value(1)
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=unbeepBoth)

def _beepOutside(time=300, num=2):
    if num <= 0:
        pinBeepOutside.value(0)
        return
    pinBeepOutside.value(not pinBeepOutside.value())
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepOutside(time, num - 1))

def beepOutside(time=300, num=2):
    pinBeepOutside.value(1)
    num *= 2
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepOutside(time, num - 1))

def _beepInside(time=300, num=2):
    if num <= 0:
        pinBeepInside.value(0)
        return
    pinBeepInside.value(not pinBeepInside.value())
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepInside(time, num - 1))

def beepInside(time=300, num=2):
    pinBeepInside.value(1)
    num *= 2
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepInside(time, num - 1))

def _beepBoth(time=300, num=2):
    if num <= 0:
        pinBeepInside.value(0)
        pinBeepOutside.value(0)
        return
    pinBeepInside.value(not pinBeepInside.value())
    pinBeepOutside.value(not pinBeepOutside.value())
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepBoth(time, num - 1))

def beepBoth(time=300, num=2):
    pinBeepInside.value(1)
    pinBeepOutside.value(1)
    num *= 2
    beepTimer.init(period=time, mode=Timer.ONE_SHOT, callback=lambda x: _beepBoth(time, num - 1))


def reboot():
    pinReset: Pin = machine.Pin(gpioconfig.REBOOT_PIN, Pin.OUT)
    pinReset.value(1)

def connectFinger():
    global fingerSession
    fingerSession = as608.connect_serial_session(gpioconfig.FINGER_UART_PORT)

def loadFinger():
    global fingerSession, fingerWakPin
    if gpioconfig.FINGER_ENABLE:
        connectFinger()
        fingerWakPin = machine.Pin(gpioconfig.FINGER_WAK_PIN, Pin.IN)
        if gpioconfig.FINGER_WAK_IRQ_ENABLE:
            fingerWakPin.irq(
                trigger=Pin.IRQ_RISING,
                handler=pinFingerWakIrqHandler
            )
        
        log.debug("finger_set_security_level: %d" % gpioconfig.FINGER_SECURITY_LEVEL)
        finger_set_security_level(gpioconfig.FINGER_SECURITY_LEVEL)


def finger_set_security_level(level):
    global fingerSession
    fingerSession.set_sysparam(5, int(level))


if gpioconfig.DOOR_MOTOR_KEEP_SIGNAL:
    def doorOpen():
        global isDoorOperating, motorPwm
        if isDoorOperating:
            return

        if isDoorForceLocked:
            log.info("Door is force locked, cannot open. Press unlock button first")
            return

        log.info("Door opened permentally")
        motorPwm.freq(gpioconfig.DOOR_MOTOR_PWM_OPEN_FREQ)
        motorPwm.duty(gpioconfig.DOOR_MOTOR_PWM_OPEN_DUTY)


    def doorClose():
        global isDoorOperating, motorPwm
        if isDoorOperating:
            return

        log.info("Door closed permentally")
        motorPwm.freq(gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ)
        motorPwm.duty(gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)


    def doorOpenAndClose():
        global isDoorOperating, motorPwm
        if isDoorOperating:
            return
        isDoorOperating = True
        if isDoorForceLocked:
            log.info("Door is force locked, cannot open. Press unlock button first")
            return
        log.info("Door unlocked, will be closed automatically after %d s" % gpioconfig.DOOR_AUTOCLOSE_DELAY)
        lightDoorAlertLed()
        motorPwm.freq(gpioconfig.DOOR_MOTOR_PWM_OPEN_FREQ)
        motorPwm.duty(gpioconfig.DOOR_MOTOR_PWM_OPEN_DUTY)
        motorPwmTimer.init(period=gpioconfig.DOOR_AUTOCLOSE_DELAY, mode=Timer.ONE_SHOT, callback=_doorOpenAndClose2)


    def _doorOpenAndClose2(timer: Timer):
        global isDoorOperating
        timer.deinit()
        motorPwm.freq(gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ)
        motorPwm.duty(gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)
        isDoorOperating = False
        unlightDoorAlertLed()
else:
    def _doorTimerDeinit(timer: Timer, pwm: PWM):
        global isDoorOperating
        pwm.deinit()
        timer.deinit()
        unlightDoorAlertLed()
        isDoorOperating = False
    
    def doorOpen():
        global isDoorOperating
        if isDoorOperating:
            return
        isDoorOperating = True
        if isDoorForceLocked:
            log.info("Door is force locked, cannot open. Press unlock button first")
            return

        log.info("Door opened permentally")
        lightDoorAlertLed()
        pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_OPEN_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_OPEN_DUTY)
        motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorTimerDeinit(x, pwm))
        pass


    def doorClose():
        global isDoorOperating
        if isDoorOperating:
            return
        isDoorOperating = True
        log.info("Door closed permentally")
        lightDoorAlertLed()
        pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)
        motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorTimerDeinit(x, pwm))
        pass


    def doorOpenAndClose():
        global isDoorOperating
        if isDoorOperating:
            return
        isDoorOperating = True
        if isDoorForceLocked:
            log.info("Door is force locked, cannot open. Press unlock button first")
            return
        log.info("Door unlocked, will be closed automatically after %d s" % gpioconfig.DOOR_AUTOCLOSE_DELAY)
        lightDoorAlertLed()
        pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_OPEN_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_OPEN_DUTY)
        motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorOpenAndClose2(x, pwm))


    def _doorOpenAndClose2(timer: Timer, pwm: PWM):
        global isDoorOperating
        pwm.deinit()
        timer.deinit()
        motorPwmTimer.init(period=gpioconfig.DOOR_AUTOCLOSE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorOpenAndClose3(x, pwm))


    def _doorOpenAndClose3(timer: Timer, pwm: PWM):
        global isDoorOperating
        pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)
        motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorTimerDeinit(x, pwm))
