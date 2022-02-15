from config import wechatconfig, httpmessagerconfig
import log
import sys

if wechatconfig.WECHAT_ENABLE:
    from messager import wechat
if httpmessagerconfig.HTTP_MESSAGER_ENABLE:
    from messager import http

def sendMessage(msg: str):
    if wechatconfig.WECHAT_ENABLE:
        try:
            wechat.sendMessage(msg)
        except Exception as e:
            log.error("Wechat: Send message failed. %s" % e)
            sys.print_exception(e)
    if httpmessagerconfig.HTTP_MESSAGER_ENABLE:
        try:
            http.sendMessage(msg)
        except Exception as e:
            log.error("HTTP: Send message failed. %s" % e)
            sys.print_exception(e)
    log.info("Message Sent: %s" % msg)