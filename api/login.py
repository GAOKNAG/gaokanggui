from common import RequestMapping, Method, Requester
from config import Config


@RequestMapping(path=Config.host)
class Login:
    @RequestMapping(path="knownjson/webInterface/", method=Method.GET)
    def login_backup(self,decice=None, events=None):
        """没事做，测试一下"""
        data = dict()
        if decice is not None:
            data["device"] = decice
        if decice == "null":
            data["device"] = None

        if events is not None:
            data["evenrs"] = events
        if events == "null":
            data["evenrs"] = events
        return Requester(headers=Config.headers,json=data)
