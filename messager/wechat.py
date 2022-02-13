import urequests as requests
from config import wechatconfig
import log
from machine import Timer

accessToken: str = ""
refreshTimer: Timer
accessTokenUrl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s"
messageUrl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s"

def refreshAccessToken(*args, **kwargs):
    global accessToken
    try:
        response = requests.get(accessTokenUrl)
        if response.status_code == 200:
            accessToken = response.json()["access_token"]
            log.info("Access token refreshed, refresh after 30min again")
            refreshTimer.init(period=30 * 60 * 1000, mode=Timer.ONE_SHOT, callback=refreshAccessToken)
        else:
            log.error("Access token refresh failed. Status code: %d" % response.status_code)
            refreshTimer.init(period=10 * 1000, mode=Timer.ONE_SHOT, callback=refreshAccessToken)
    except Exception as e:
        log.error("Access token refresh failed: %s" % str(e))
        refreshTimer.init(period=10 * 1000, mode=Timer.ONE_SHOT, callback=refreshAccessToken)

def sendMessage(msg: str):
    if not wechatconfig.WECHAT_ENABLE:
        return False

    currentMsgUrl = messageUrl % accessToken
    body = {
        "touser" : "@all",
        "toparty" : "",
        "totag" : "",
        "msgtype" : "text",
        "agentid" : int(wechatconfig.WECHAT_AGENTID),
        "text" : {
            "content" : msg
        },
        "safe":0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    
    response = requests.post(url=currentMsgUrl, json=body)
    if response.status_code >= 200 and response.status_code < 300:
        return True
    else:
        log.error("Wechat message send failed. Status code: %d" % response.status_code)
        return False


def start():
    global accessTokenUrl, refreshTimer
    if wechatconfig.WECHAT_ENABLE:
        log.info("Starting wechat messager")
        refreshTimer = Timer(-1)
        accessTokenUrl = accessTokenUrl % (wechatconfig.WECHAT_CORPID, wechatconfig.WECHAT_CORPSECRET)
        refreshAccessToken()