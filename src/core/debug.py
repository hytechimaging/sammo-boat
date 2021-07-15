# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from datetime import datetime

DEBUG_FILE_NAME = "Sammo.log"


class Debug:
    @staticmethod
    def log(msg: str):
        Debug._log("LOG", msg)

    @staticmethod
    def warning(msg: str):
        Debug._log("WARNING", msg)

    @staticmethod
    def error(msg: str):
        Debug._log("ERROR", msg)

    @staticmethod
    def _log(prefix: str, msg: str):
        print(prefix + " - " + msg)
        with open(DEBUG_FILE_NAME, "a") as file:
            file.write(
                Debug.nowToString() + " - " + prefix + " - " + msg + "\n"
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
