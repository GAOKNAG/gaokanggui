import logging
import sys
from config import Config


class Logger(object):

    def __init__(self, filename=Config.log_name):
        self.logger = logging.getLogger(filename)
        formatter = logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s")
        "文件日志"
        file_handler = logging.FileHandler(filename=Config.log_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        "控制日志"
        console_hanler = logging.StreamHandler(sys.stdout)
        console_hanler.formatter = formatter
        "为logger添加的日志处理器"
        if file_handler.baseFilename not in \
                [x.baseFilenmae for x in self.logger.handlers if getattr(x, "baseFilenme", False)]:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_hanler)
        self.logger.setLevel(logging.INFO)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def war(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


if __name__ == '__main__':
    logger = Logger()
    logger.info("111")
