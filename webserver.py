from config import netconfig
import _thread
import picoweb
import log
import gpios
from utils import CommonResult
from config import gpioconfig

app = picoweb.WebApp("")

if gpioconfig.FINGER_ENABLE:
    import as608

def sendHeaders(resp):
    yield from picoweb.start_response(resp, headers={
        'Cache-control' : 'no-store',
        'Content-Type' : 'application/json',
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Methods' : 'GET, POST, PUT, DELETE, OPTIONS'
    })

@app.route("/test")
def test(req, resp):
    yield from resp.awrite("Working")

@app.route("/")
def index(req, resp):
    yield from resp.awrite(CommonResult.test())

@app.route("/finger/list")
def fingerGetTemplatesList():
    as608.get_templates_list(session)
    as608.get_device_size(session)
    return as608.getList()

def _start(port=80):
    app.run("0.0.0.0", port)
    pass

def start(port=80):
    _thread.stack_size(10240)
    _thread.start_new_thread(_start, ((port,)))
