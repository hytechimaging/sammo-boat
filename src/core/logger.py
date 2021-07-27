# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from datetime import datetime
from qgis.core import QgsMessageLog

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
        msg = "{} - {}".format(prefix, msg)
        QgsMessageLog.logMessage(msg, "Sammo-Boat")
        with open(LOG_FILE_NAME, "a") as file:
            file.write("{} - {}\n".format(Logger.nowToString(), msg))

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
