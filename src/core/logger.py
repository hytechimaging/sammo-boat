# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from datetime import datetime

LOG_FILE_NAME = "Sammo.log"


class Logger:
    @staticmethod
    def log(msg: str):
        Logger._log("LOG", msg)

    @staticmethod
    def warning(msg: str):
        Logger._log("WARNING", msg)

    @staticmethod
    def error(msg: str):
        Logger._log("ERROR", msg)

    @staticmethod
    def _log(prefix: str, msg: str):
        print(prefix + " - " + msg)
        with open(LOG_FILE_NAME, "a") as file:
            file.write(
                Logger.nowToString() + " - " + prefix + " - " + msg + "\n"
            )

    @staticmethod
    def nowToString() -> str:
        dateTimeObj = datetime.now()
        time = (
            "{:02d}".format(dateTimeObj.hour)
            + ":"
            + "{:02d}".format(dateTimeObj.minute)
            + ":"
            + "{:02d}".format(dateTimeObj.second)
        )
        return time
