# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from time import sleep
from .session import SammoSession


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    isNeedToContinue = True

    def __init__(self, testFilePath: str, session: SammoSession):
        super().__init__()
        self._testFilePath = testFilePath
        self._session: SammoSession = session

    def run(self):
        with open(self._testFilePath) as file:
            lines = file.readlines()

        while True:
            for line in lines:
                sleep(1)
                if (False == self.isNeedToContinue):
                    break
                coordinates = line.strip().split(';')
                longitude_deg = coordinates[0]
                latitude_deg = coordinates[1]

                self._session.addNewFeatureToGpsTable(longitude_deg, latitude_deg)
                self.progress.emit("Coordonnées GPS : longitude = {}° - latitude = {}°".format(longitude_deg, latitude_deg))

        self.finished.emit()

    def stop(self):
        self.isNeedToContinue = False


class ThreadGps:
    def __init__(self, session: SammoSession):
        self._session: SammoSession = session

    def start(self, testFilePath: str):
        self.thread = QThread()
        self.worker = Worker(testFilePath, self._session)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)

        self.thread.start()

    def stop(self):
        self.worker.stop()

    def reportProgress(self, u: str):
        print("Progress : " + u)
