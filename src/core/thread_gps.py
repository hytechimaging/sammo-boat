# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from .session import SammoSession
from datetime import datetime


class WorkerGps(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float)

    def __init__(self, testFilePath: str, session: SammoSession):
        super().__init__()
        self._testFilePath = testFilePath
        self._session: SammoSession = session
        self._lines = None

    def _toDoInsideLoop(self):
        for line in self._lines:
            sleep(1)
            if self._isNeedToStop:
                return
            coordinates = line.strip().split(";")
            longitude_deg = coordinates[0]
            latitude_deg = coordinates[1]

            self.addNewFeatureToGpsTableSignal.emit(
                float(longitude_deg), float(latitude_deg)
            )
            self._log(
                "Coordonnées GPS : longitude = {}°"
                " - latitude = {}°".format(longitude_deg, latitude_deg)
            )

    def _onStart(self):
        with open(self._testFilePath) as file:
            lines = file.readlines()
        return lines


class ThreadGps(OtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str)

    def __init__(self, session: SammoSession):
        super().__init__()
        self._session: SammoSession = session

    def start(self, testFilePath: str):
        worker = WorkerGps(testFilePath, self._session)
        worker.addNewFeatureToGpsTableSignal.connect(
            self.addNewFeatureToGpsTable
        )
        super().start(worker)

    def addNewFeatureToGpsTable(
        self, longitude_deg: float, latitude_deg: float
    ):
        self.addNewFeatureToGpsTableSignal.emit(longitude_deg, latitude_deg, self.nowToString())

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
