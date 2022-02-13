import urequests as requests
import log
from config import httpmessagerconfig


def sendMessage(msg: str):
    global accessToken
    with requests.post(httpmessagerconfig.HTTP_MESSAGER_URL, data={"content": msg}) as response:
        if response.status_code >= 200 and response.status_code < 300:
            return True
        else:
            log.error("Send message failed. Status code: %d" % response.status_code)
            return False
