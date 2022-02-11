# Device Common Config
DEVICE_NAME = "FingerDoorController"

# STA Mode Config
STA_SSID = ""
STA_WPA_KEY = ""
STA_DHCP = True
# STA_STATIC_* is only used when STA_DHCP is False
STA_STATIC_IP = "192.168.1.22"
STA_STATIC_MASK = "255.255.255.0"
STA_STATIC_GATEWAY = "192.168.1.1"

# AP Mode Config
AP_WPA_KEY = ""
AP_GATEWAY = "192.168.212.1"
AP_IP = "192.168.212.1"
AP_DNS = "223.5.5.5"

# NTP Config
NTP_HOST = "ntp.aliyun.com"
TIMEZONE_DELTA = 3155644800