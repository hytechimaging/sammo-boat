# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import serial
from time import sleep
from typing import Optional
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from .session import SammoSession
from datetime import datetime


class WorkerSimuGps(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str, float, float)

    def __init__(
        self,
        testFilePath: str,
        session: SammoSession,
        indexOfNextGpsPoint: int,
    ):
        super().__init__()
        self._gps: Optional[serial.Serial] = serial.Serial()
        self._testFilePath = testFilePath
        self._session: SammoSession = session
        self._lines = None
        self._indexOfNextGpsPoint = indexOfNextGpsPoint

    def _toDoInsideLoop(self):
        nbLines = len(self._lines)
        for i in range(self._indexOfNextGpsPoint, nbLines):
            sleep(1)
            if self._isNeedToStop:
                return

            infos = self._lines[i].strip().split(",")
            latitude_deg = infos[0]
            longitude_deg = infos[1]
            formattedDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            speed = -9999.0
            course = -9999.0
            if len(infos) == 6 and infos[4] and infos[5]:
                speed = infos[4]
                course = infos[5]

            self.addNewFeatureToGpsTableSignal.emit(
                float(longitude_deg),
                float(latitude_deg),
                formattedDateTime,
                float(speed),
                float(course),
            )
            self._log(
                "GPS : longitude = {}°"
                " - latitude = {}° - datetime = {}".format(
                    longitude_deg, latitude_deg, formattedDateTime
                )
            )
            self._indexOfNextGpsPoint = self._indexOfNextGpsPoint + 1

        # always begins at the second line because the first is for titles
        self._indexOfNextGpsPoint = 1

    def _onStart(self):
        with open(self._testFilePath) as file:
            self._lines = file.readlines()

    @staticmethod
    def _removeQuotes(strValue: str) -> str:
        strLen = len(strValue)
        if strValue[0] == '"' and strValue[strLen - 1] == '"':
            strValue = strValue[1 : strLen - 1]
        return strValue


class ThreadSimuGps(OtherThread):
    frame = pyqtSignal(float, float, int, int, int, float, float)

    def __init__(self, session: SammoSession, testFilePath: str):
        super().__init__()
        self._session: SammoSession = session
        self._testFilePath = testFilePath
        # always begins at the second line because the first is for titles
        self.indexOfNextGpsPoint: int = 1
        self.worker = None

    def start(self):
        self.worker = WorkerSimuGps(
            self._testFilePath,
            self._session,
            self.indexOfNextGpsPoint,
        )
        self.worker.addNewFeatureToGpsTableSignal.connect(self.newFrame)
        super()._start(self.worker)

    def stop(self):
        self.indexOfNextGpsPoint = self.worker._indexOfNextGpsPoint
        super().stop()

    @staticmethod
    def getDatetime(line: str) -> (int, int, int):
        # "2021-10-28 15:32:10"
        components = line.split(" ")
        time = components[1].split(":")
        hour = int(time[0])
        minutes = int(time[1])
        secondes = int(time[2])
        return hour, minutes, secondes

    def newFrame(
        self,
        longitude_deg: float,
        latitude_deg: float,
        formattedDateTime: str,
        speed: float,
        course: float,
    ):
        self.frame.emit(
            longitude_deg,
            latitude_deg,
            *self.getDatetime(formattedDateTime),
            speed,
            course
        )

    @staticmethod
    def nowToString() -> str:
        dateTimeObj = datetime.now()
        time = (
            "{:02d}".format(dateTimeObj.day)
            + "/"
            + "{:02d}".format(dateTimeObj.month)
            + "/"
            + str(dateTimeObj.year)
            + " "
            + "{:02d}".format(dateTimeObj.hour)
            + ":"
            + "{:02d}".format(dateTimeObj.minute)
            + ":"
            + "{:02d}".format(dateTimeObj.second)
        )
        return time
