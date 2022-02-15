from config import wechatconfig, httpmessagerconfig
import log

if wechatconfig.WECHAT_ENABLE:
    from messager import wechat
if httpmessagerconfig.HTTP_MESSAGER_ENABLE:
    from messager import http

def sendMessage(msg: str):
    if wechatconfig.WECHAT_ENABLE:
        wechat.sendMessage(msg)
    if httpmessagerconfig.HTTP_MESSAGER_ENABLE:
        http.sendMessage(msg)
    log.info("Message Sent: %s" % msg)