import re
from machine import Pin
import machine
from config import gpioconfig
import log

tmd = None
pinStatus: Pin 
pinBootButton: Pin
pinBootButtonIrqHandler = lambda _: log.debug("Button Boot Pressed")

def loadPin():
    global pinStatus, pinBootButton, pinLight, pinBootButtonIrqHandler
    pinStatus: Pin = machine.Pin(gpioconfig.LED_STATUS_PIN, Pin.OUT)
    pinBootButton: Pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    pinBootButton.irq(
        trigger=Pin.IRQ_FALLING, 
        handler=pinBootButtonIrqHandler
    )


def reboot():
    pinReset: Pin = machine.Pin(gpioconfig.REBOOT_PIN, Pin.OUT)
    pinReset.value(1)
