import datetime
import os
import uuid


class Config:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    host = "http://www.bejson.com/"
    headers = {}
    log_name = "log{}.log".format(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S"))
    rerun = 1
    log_path = os.path.join(ROOT, "logs", log_name)
    allure_report = os.path.join(ROOT, "result", "allure_report")
    html_report = os.path.join(ROOT, "result", "index.html")


if __name__ == '__main__':
    print(Config.ROOT)
