# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from .session import SammoSession
from datetime import datetime


class WorkerSimuGps(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str)

    def __init__(
        self,
        testFilePath: str,
        session: SammoSession,
        indexOfNextGpsPoint: int,
    ):
        super().__init__()
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

            coordinates = self._lines[i].strip().split(",")
            latitude_deg = coordinates[0]
            longitude_deg = coordinates[1]
            formattedDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.addNewFeatureToGpsTableSignal.emit(
                float(longitude_deg), float(latitude_deg), formattedDateTime
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
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str)

    def __init__(self, session: SammoSession, testFilePath: str):
        super().__init__()
        self._session: SammoSession = session
        self._testFilePath = testFilePath
        # always begins at the second line because the first is for titles
        self.indexOfNextGpsPoint: int = 1

    def start(self):
        self.worker = WorkerSimuGps(
            self._testFilePath, self._session, self.indexOfNextGpsPoint
        )
        self.worker.addNewFeatureToGpsTableSignal.connect(
            self.addNewFeatureToGpsTable
        )
        super()._start(self.worker)

    def stop(self):
        self.indexOfNextGpsPoint = self.worker._indexOfNextGpsPoint
        super().stop()

    def addNewFeatureToGpsTable(
        self, longitude_deg: float, latitude_deg: float, formattedDateTime: str
    ):
        self.addNewFeatureToGpsTableSignal.emit(
            longitude_deg, latitude_deg, formattedDateTime
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
