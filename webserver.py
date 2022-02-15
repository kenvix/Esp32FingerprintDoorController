from config import netconfig
import _thread
import picoweb
import log
import gpios
from utils import CommonResult
from config import gpioconfig
import door
from config import functionconfig
from messager import messager

app = picoweb.WebApp("")

if gpioconfig.FINGER_ENABLE:
    import as608

def sendHeaders(resp):
    yield from picoweb.start_response(resp, headers={
        'Cache-control' : 'no-store',
        'Content-Type' : 'application/json',
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Methods' : 'GET, POST, PUT, DELETE, OPTIONS',
    })


@app.route("/test")
def test(req, resp):
    yield from resp.awrite("Working")

@app.route("/")
def index(req, resp):
    yield from resp.awrite(CommonResult.test())


@app.route("/finger")
def fingerAdd(req, resp):
    yield from resp.awrite(CommonResult(0, "OK", {
        "isFingerEnabled" : gpioconfig.FINGER_ENABLE,
        "fingerPin": gpioconfig.FINGER_WAK_PIN,
        "fingerUartPort": gpioconfig.FINGER_UART_PORT,
        "fingerSecurityLevel": gpioconfig.FINGER_SECURITY_LEVEL,
        "isFingerWakIrqEnabled": gpioconfig.FINGER_WAK_IRQ_ENABLE,
        "isFingerDetecting" : door.isFingerDetecting,
        "isFingerDetectionShouldStop": door.isFingerDetectionShouldStop,
        "isFingerAdding": door.isFingerAdding,
        "lastInsertedLocation": gpios.fingerSession.last_inserted_location,
        "lastInsertedTime": log.nowInString(door.fingerLastInsertedTime),
    }).toJSON())

@app.route("/finger/list")
def fingerGetTemplatesList(req, resp):
    yield from resp.awrite(CommonResult(0, "OK", {
        "templates" : as608.get_templates_list(gpios.fingerSession),
        "capacity" : int(as608.get_device_size(gpios.fingerSession)),
    }).toJSON())


@app.route("/finger/add")
def fingerAdd(req, resp):
    try:
        door.addFingerAsync()
        yield from resp.awrite(CommonResult(0, "Prepared to add finger, put your finger now.").toJSON())
    except Exception as e:
        yield from resp.awrite(CommonResult(500, "Failed to add finger: %s" % e).toJSON())


@app.route("/finger/delete")
def fingerAdd(req, resp):
    try:
        if 'id' in req.form:
            door.deleteFinger(req.form['id'])
            yield from resp.awrite(CommonResult(0, "Deleted finger %d" % req.form['id']).toJSON())
        else:   
            yield from resp.awrite(CommonResult(400, "Missing param id.").toJSON())
    except Exception as e:
        yield from resp.awrite(CommonResult(500, "Failed to delete finger: %s" % e).toJSON())



@app.route("/door")
def doorInfo(req, resp):
    gpios.doorOpenAndClose()
    yield from resp.awrite(CommonResult(0, "see also: /door/unlock, /door/open, /door/close", {
        "autoClose_Delay" : gpioconfig.DOOR_AUTOCLOSE_DELAY,
        "isMotorEnabled" : gpioconfig.DOOR_MOTOR_ENABLE,
        "isDoorOperating" : gpios.isDoorOperating,
        "motorPin": gpioconfig.DOOR_MOTOR_PIN,
        "directOpenPin": gpioconfig.DOOR_DIRECT_PIN_OPEN,
        "directClosePin": gpioconfig.DOOR_DIRECT_PIN_CLOSE,
        "directRolltateDelay": gpioconfig.DOOR_DIRECT_ROLLTATE_DELAY,
        "isBeepEnabled" : gpioconfig.BEEP_OUTSIDE_PIN != None,
        "beepOutsidePin": gpioconfig.BEEP_OUTSIDE_PIN,
        "beepInsidePin": gpioconfig.BEEP_INSIDE_PIN,
    }).toJSON())


@app.route("/door/unlock")
def doorUnlock(req, resp):
    gpios.doorOpenAndClose()
    yield from resp.awrite(CommonResult(0, "Door unlocked, will be closed automatically after %d s" % gpioconfig.DOOR_AUTOCLOSE_DELAY, None).toJSON())
    if functionconfig.DOOR_MESSAGE_ENABLE:
        messager.sendMessage(functionconfig.DOOR_MESSAGE_CONTENT % (log.nowInString(), "HTTP API", "N/A", "正常开门"))


@app.route("/door/open")
def doorOpen(req, resp):
    gpios.doorOpen()
    yield from resp.awrite(CommonResult(0, "Door opened permentally", None).toJSON())
    if functionconfig.DOOR_MESSAGE_ENABLE:
        messager.sendMessage(functionconfig.DOOR_MESSAGE_CONTENT % (log.nowInString(), "HTTP API", "N/A", "Door opened permentally"))



@app.route("/door/close")
def doorClose(req, resp):
    gpios.doorClose()
    yield from resp.awrite(CommonResult(0, "Door closed permentally", None).toJSON())
    if functionconfig.DOOR_MESSAGE_ENABLE:
        messager.sendMessage(functionconfig.DOOR_MESSAGE_CONTENT % (log.nowInString(), "HTTP API", "N/A", "Door closed permentally"))


def _start(port=80):
    app.run("0.0.0.0", port)
    pass

def start(port=80):
    _thread.stack_size(10240)
    _thread.start_new_thread(_start, ((port,)))
