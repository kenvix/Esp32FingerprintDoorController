import gpios
import log
import as608

def addFinger():
    log.info("Adding finger")
    as608.enroll_finger_to_device(gpios.fingerSession, as608)

def _doorFingerWakIrqHandler(pin):
    log.debug("Finger wak pin pressed")

def startDoorController():
    log.info("Starting door controller")
    gpios.pinFingerWakIrqHandler = _doorFingerWakIrqHandler