import re
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
pinFingerWakIrqHandler = lambda _: log.debug("Finger wak pin pressed")

def loadPin():
    global pinStatus, pinBootButton, pinLight, pinBootButtonIrqHandler, fingerSession, fingerWakPin, timerStatus
    pinStatus: Pin = machine.Pin(gpioconfig.LED_STATUS_PIN, Pin.OUT)
    pinBootButton: Pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    pinBootButton.irq(
        trigger=Pin.IRQ_FALLING, 
        handler=pinBootButtonIrqHandler
    )
    timerStatus = Timer(-1)

def blinkStatusLED():
    timerStatus.init(period=350, mode=Timer.PERIODIC, callback=lambda x: pinStatus.value(not pinStatus.value()))

def cancelBlinkStatusLED():
    timerStatus.deinit()

def reboot():
    pinReset: Pin = machine.Pin(gpioconfig.REBOOT_PIN, Pin.OUT)
    pinReset.value(1)

def loadFinger():
    if gpioconfig.FINGER_ENABLE:
        fingerSession = as608.connect_serial_session(gpioconfig.FINGER_UART_PORT)
        fingerWakPin = machine.Pin(gpioconfig.FINGER_WAK_PIN, Pin.IN)
        if gpioconfig.FINGER_WAK_IRQ_ENABLE:
            fingerWakPin.irq(
                trigger=Pin.IRQ_RISING, 
                handler=pinFingerWakIrqHandler
            )


def doorOpen():
    pass

def doorClose():
    pass

def startDoorController():
    log.info("Starting door controller")
