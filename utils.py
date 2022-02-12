import json

class CommonResult:
    def __init__(self, status, info, data):
        self.obj = {
            "status" : int(status),
            "info" : str(info),
            "data" : data
        }
    
    def toJSON(self):
        return json.dumps(self.obj)

    def __str__(self):
        return "status: %d, info: %s, data: %s" % (self.obj.code, self.obj.info, str(self.obj.data))

    @staticmethod
    def test():
        return CommonResult(0, "Written by Kenvix @ 2022 For AI+Mobile Lab. OpenSource Project. Licensed under GPLv3.", {"see": "https://kenvix.com"}).toJSON()


if __name__ == "__main__":
    print(CommonResult.test())