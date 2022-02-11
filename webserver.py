from config import netconfig
import _thread
import picoweb
import log
import gpios

app = picoweb.WebApp(netconfig.DEVICE_NAME)

@app.route("/")
def index(req, resp):
    yield from resp.awrite("Working")

htmlText: str

def returnLightSwitchHTML(req, resp, state):
    yield from picoweb.start_response(resp, headers={
        'Cache-control' : 'no-store'
    })
    
    now = log.nowInString()
    yield from resp.awrite(htmlText.replace("{{$currentTime}}", now).replace("{{$currentState}}", state))


@app.route("/light")
def index(req, resp):
    yield from returnLightSwitchHTML(req, resp, gpios.getLightState())

@app.route("/light/switch")
def index(req, resp):
    gpios.switchLight()
    yield from returnLightSwitchHTML(req, resp, gpios.getLightState())
    

def _start(port=80):
    app.run("0.0.0.0", port)
    pass

def start(port=80):
    global htmlText
    htmlFile = open('static/gpio.html', 'r')
    htmlText = htmlFile.read()
    _thread.start_new_thread(_start, ((port,)))