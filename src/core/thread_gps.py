# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from .session import SammoSession


class WorkerGps(WorkerForOtherThread):
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

            self._session.addNewFeatureToGpsTable(longitude_deg, latitude_deg)
            self._log(
                "Coordonnées GPS : longitude = {}°"
                " - latitude = {}°".format(longitude_deg, latitude_deg)
            )

    def _onStart(self):
        with open(self._testFilePath) as file:
            lines = file.readlines()
        return lines


class ThreadGps(OtherThread):
    def __init__(self, session: SammoSession):
        self._session: SammoSession = session

    def start(self, testFilePath: str):
        worker = WorkerGps(testFilePath, self._session)
        super().start(worker)
