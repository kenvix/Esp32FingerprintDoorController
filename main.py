import gpios
gpios.loadPin()
gpios.blinkStatusLED()

from config import functionconfig
import os
import sys
import log
import machine
import network
from config import netconfig
from config import gpioconfig
import time
import install
from network import WLAN
from lib import ftp_thread
import uos
import ntptime
import utils
from machine import Timer
import _thread
from machine import Pin
import gc

gc.collect()
import webserver
gc.collect()

sta_if: WLAN = None
ap_if: WLAN = None

timer_ntp: Timer = None
timer_wlan: Timer = None
timer_gc: Timer = None

def test(*args, **kwargs):
    print("Test! args: %s    kwargs: %s" % (str(args), str(kwargs)))

def df():
    s = os.statvfs('//')
    return ('{0} MB'.format((s[0]*s[3])/1048576))

def reboot():
    try:
        if gpioconfig.REBOOT_PIN is not None:
            log.info("Reset pin found, hard rebooting")
            gpios.reboot()
        else:
            raise NameError("No reset pin defined")
    except Exception:
        log.warn("No reset pin defined, using soft reboot")
        machine.reset()


def free(full=True):
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = '{0:.2f}%'.format(F/T*100)
    if not full:
        return P
    else:
        return ('Total:{0} Free:{1} ({2})'.format(T, F, P))


def setupAP():
    log.info("Setting up AP with SSID %s     Key %s" %
             (netconfig.DEVICE_NAME, netconfig.AP_WPA_KEY))
    global ap_if
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid=netconfig.DEVICE_NAME, password=netconfig.AP_WPA_KEY)
    if len(netconfig.AP_WPA_KEY) > 8:
        ap_if.config(authmode=network.AUTH_WPA_WPA2_PSK)
    else:
        log.warn("No AP password set or password is too short")

    # No network, not a gateway
    ap_if.ifconfig((netconfig.AP_IP, '255.255.255.0',
                    netconfig.AP_GATEWAY, netconfig.AP_DNS))
    log.info("AP Config: %s" % str(ap_if.ifconfig()))


def setupmDNS(local_addr):
    if functionconfig.MDNS_ENABLE:
        from lib import slimDNS
        server = slimDNS.SlimDNSServer(local_addr, netconfig.DEVICE_NAME.lower())
        _thread.start_new_thread(server.run_forever, ())


def waitAPUp():
    global ap_if
    while ap_if.active() == False:
        time.sleep(0.3)
        pass
    log.info("AP %s is up" % netconfig.DEVICE_NAME)


def setupFTP():
    log.info("Starting FTP")
    try:
        _thread.start_new_thread(ftp_thread.ftpserver, ((True,)))
    except:
        ftp_thread.ftpserver(False)


def setupSTA():
    global sta_if
    if len(netconfig.STA_SSID) < 1:
        log.info("STA not configured, skip")
    else:
        log.info("Setting up STA with SSID %s     Key %s" %
                 (netconfig.STA_SSID, netconfig.STA_WPA_KEY))
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)

def flashmode():
    os.remove("main.py")
    machine.reset()

def forceflash():
    os.remove("project.pymakr")
    flashmode()

def waitSTAUp():
    global sta_if
    if sta_if is not None:
        while True:
            # waitScan = True
            # while waitScan:
            #     try:
            #         scanResults = sta_if.scan()
            #         for scanResult in scanResults:
            #             ssid = scanResult[0].decode()
            #             log.trace("Scan: %s : %s" % (ssid, str(scanResult)))
            #             if ssid == netconfig.STA_SSID:
            #                 log.info("Target STA SSID exist. Continue")
            #                 waitScan = False
            #                 break
                    
            #         if waitScan == True:
            #             log.info("Target STA SSID NOT exist. Waiting")
            #             time.sleep(10)
            #     except Exception as e:
            #         log.error("STA scan failed: %s" % str(e))
            waitCount = 0

            try:
                sta_if.connect(netconfig.STA_SSID, netconfig.STA_WPA_KEY)
            except Exception as e:
                log.error("STA connection failed: %s" % str(e))
                waitCount = 99999

            while sta_if.isconnected() == False and waitCount < 60:
                time.sleep(0.3)
                waitCount += 1
                pass

            if waitCount >= 60:
                log.error("STA connection failed. retry")
                showDigital(' sta')
                try:
                    sta_if.disconnect()
                except Exception:
                    pass
            else:
                gpios.unlightWlanAlertLed()
                log.info("STA %s is up" % netconfig.STA_SSID)
                log.info("STA Connection info: %s" % str(sta_if.ifconfig()))
                return 


def _watchSTAConnection(*args, **kwargs):
    if not sta_if.isconnected():
        log.warn("STA connection lost.")
        gpios.lightWlanAlertLed()
        try:
            sta_if.disconnect()
            waitSTAUp()
        except Exception:
            pass
    
    timer_wlan.init(period=8000, mode=Timer.ONE_SHOT, callback=_watchSTAConnection)


def watchSTAConnection():
    global sta_if, timer_wlan
    if sta_if is not None:
        if timer_wlan is None:
            timer_wlan = Timer(-1)
            _watchSTAConnection()


def _runNTP(*args, **kwargs):
    try:
        log.info("NTP Syncing")
        ntptime.NTP_DELTA = netconfig.TIMEZONE_DELTA   # 可选 UTC+8偏移时间（秒），不设置就是UTC0
        ntptime.host = netconfig.NTP_HOST  # 可选，ntp服务器，默认是"pool.ntp.org"
        ntptime.settime()   # 修改设备时间,到这就已经设置好了
        log.info("NTP time synced. Sync again after 6h")
        timer_ntp.init(period=6 * 60 * 60 * 1000, mode=Timer.ONE_SHOT, callback=_runNTP)
    except Exception as e:
        log.error("NTP time Sync failed, retry after 3s")
        sys.print_exception(e, sys.stderr)
        timer_ntp.init(period=3000, mode=Timer.ONE_SHOT, callback=_runNTP)


def setupNTP():
    global sta_if, timer_ntp
    if sta_if is None:
        log.warn("STA not configured, skip NTP client")
    else:
        if timer_ntp is None:
            timer_ntp = Timer(-1)
            _runNTP()


def setupDigitalClock():
    if gpioconfig.LED_TM1637_ENABLE:
        from lib import tm1637
        gpios.tmd = tm1637.TM1637(clk=Pin(gpioconfig.LED_TM1637_PIN_CLK),
                            dio=Pin(gpioconfig.LED_TM1637_PIN_DIO))
    else:
        gpios.tmd = None


def showDigital(s):
    if gpios.tmd is not None:
        gpios.tmd.show(s)


def _keepShowTime():
    showColon = True
    while True:
        n = log.now()
        gpios.tmd.numbers(n[4], n[5], colon=showColon)
        showColon = not showColon
        time.sleep(3)


def keepShowTime():
    if gpioconfig.LED_TM1637_ENABLE and gpios.tmd is not None:
        _thread.start_new_thread(_keepShowTime, ())


def _boot(*args, **kwargs):
    if gpioconfig.LED_TM1637_ENABLE is True:
        setupDigitalClock()
        showDigital('gpio')

    try:
        showDigital('ap  ')
        setupAP()
        waitAPUp()
        log.info("Starting mDNS for AP")
        setupmDNS(ap_if.ifconfig()[0])
    except Exception as e:
        log.error("Setup Wi-FI AP FAILED!")
        sys.print_exception(e, sys.stderr)

    try:
        showDigital('ftp ')
        setupFTP()
    except Exception as e:
        log.error("Setup FTP server FAILED!")
        sys.print_exception(e, sys.stderr)
    
    try:
        showDigital('teln')
        # utelnetserver.start()
    except Exception as e:
        log.error("Setup Telnet server FAILED!")
        sys.print_exception(e, sys.stderr)

    try:
        showDigital('sta ')
        gpios.lightWlanAlertLed()
        setupSTA()
        waitSTAUp()
        watchSTAConnection()
        log.info("Starting mDNS for STA")
        setupmDNS(sta_if.ifconfig()[0])
    except Exception as e:
        log.error("Setup Wi-FI STA FAILED!")
        sys.print_exception(e, sys.stderr)

    log.enableSyslog()
    
    try:
        showDigital('http')
        log.info("Starting http server")
        webserver.start()
    except Exception as e:
        log.error("Setup HTTP server FAILED!")
        sys.print_exception(e, sys.stderr)

    showDigital('ntp ')
    setupNTP()
    keepShowTime()

    if gpioconfig.FINGER_ENABLE:
        gpios.loadFinger()
        import door
        if gpioconfig.DOOR_DIRECT_ENABLE or gpioconfig.DOOR_MOTOR_ENABLE:
            door.startDoorController()
        door.startFingerKeepAlive()

    gc.collect()
    gpios.cancelBlinkStatusLED()
    gpios.beepOutsideOnce(180)
    global timer_gc
    timer_gc = Timer(-1)
    timer_gc.init(period=60 * 1000, mode=Timer.PERIODIC, callback=lambda t: gc.collect())
    

def main():
    log.info("Kenvix Fingerprint Door Controller v1.0")
    log.info("System info: %s" % str(os.uname()))
    gc.enable()
    gc.collect()
    boot_timer = Timer(-1)
    boot_timer.init(period=100, mode=Timer.ONE_SHOT, callback=_boot)
    pass


if __name__ == "__main__":
    main()
