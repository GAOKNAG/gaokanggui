import jsonpath as jsonpath
import pytest
import requests
from config import Config
from api.login import Login


@pytest.mark.run(order=1)
class Testactivity:
    @pytest.mark.parametrize("decice", ["xiaomi"])
    @pytest.mark.parametrize("events", ["test"])
    def test_login_qq(self, decice, events):
        api = Login()
        res = api.login_backup(decice=decice, events=events)

