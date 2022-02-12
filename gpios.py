from machine import Timer
from machine import Pin
import machine
from config import gpioconfig
import log
from serial import Serial
from machine import PWM

if gpioconfig.FINGER_ENABLE:
    import as608

tmd = None
pinStatus: Pin
timerStatus: Timer
pinBootButton: Pin
pinBootButtonIrqHandler = lambda _: log.debug("Button Boot Pressed")
fingerSession: Serial = None
fingerWakPin: Pin = None
isDoorOperating = False
pinFingerWakIrqHandler = lambda _: log.debug("Finger wak pin pressed")
pinMotor: Pin
motorPwmTimer = Timer(1)


def loadPin():
    global pinStatus, pinBootButton, pinLight, pinBootButtonIrqHandler, fingerSession, fingerWakPin, timerStatus, pinMotor
    pinStatus: Pin = machine.Pin(gpioconfig.LED_STATUS_PIN, Pin.OUT)
    pinStatus.value(0)
    pinBootButton: Pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    pinBootButton.irq(
        trigger=Pin.IRQ_FALLING,
        handler=pinBootButtonIrqHandler
    )
    # timerStatus = None
    timerStatus = Timer(-1)
    if gpioconfig.DOOR_MOTOR_ENABLE:
        pinMotor: Pin = machine.Pin(gpioconfig.DOOR_MOTOR_PIN, Pin.OUT)

# def blinkStatusLED(freq = 3, duty = 20):
#     global timerStatus
#     if timerStatus is not None:
#         timerStatus.deinit()

#     timerStatus = PWM(pinStatus, freq=freq, duty=duty)
#     return timerStatus


def blinkStatusLED(period=350):
    global timerStatus
    timerStatus.init(period=period, mode=Timer.PERIODIC, callback=lambda x: pinStatus.value(not pinStatus.value()))
    return timerStatus


def cancelBlinkStatusLED():
    global timerStatus
    timerStatus.deinit()


def reboot():
    pinReset: Pin = machine.Pin(gpioconfig.REBOOT_PIN, Pin.OUT)
    pinReset.value(1)


def loadFinger():
    global fingerSession, fingerWakPin
    if gpioconfig.FINGER_ENABLE:
        fingerSession = as608.connect_serial_session(
            gpioconfig.FINGER_UART_PORT)
        fingerWakPin = machine.Pin(gpioconfig.FINGER_WAK_PIN, Pin.IN)
        if gpioconfig.FINGER_WAK_IRQ_ENABLE:
            fingerWakPin.irq(
                trigger=Pin.IRQ_RISING,
                handler=pinFingerWakIrqHandler
            )

def _doorTimerDeinit(timer: Timer, pwm: PWM):
    global isDoorOperating
    pwm.deinit()
    timer.deinit()
    isDoorOperating = False


def doorOpen():
    global isDoorOperating
    if isDoorOperating:
        return
    isDoorOperating = True
    pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_OPEN_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_OPEN_DUTY)
    motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorTimerDeinit(x, pwm))
    pass


def doorClose():
    global isDoorOperating
    if isDoorOperating:
        return
    isDoorOperating = True
    pwm = PWM(pinMotor, freq=gpioconfig.DOOR_MOTOR_PWM_CLOSE_FREQ, duty=gpioconfig.DOOR_MOTOR_PWM_CLOSE_DUTY)
    motorPwmTimer.init(period=gpioconfig.DOOR_MOTOR_ROLLTATE_DELAY, mode=Timer.ONE_SHOT, callback=lambda x: _doorTimerDeinit(x, pwm))
    pass


def doorOpenAndClose():
    global isDoorOperating
    if isDoorOperating:
        return
    isDoorOperating = True
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


def startDoorController():
    log.info("Starting door controller")
