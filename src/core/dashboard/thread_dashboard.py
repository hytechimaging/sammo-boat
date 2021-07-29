# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from ..other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from datetime import datetime


class WorkerDashboard(WorkerForOtherThread):
    updateTimerSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lines = None

    def _toDoInsideLoop(self):
        while not self._isNeedToStop:
            sleep(1)
            self.updateTimerSignal.emit()

    def _onStart(self):
        pass


class ThreadDashboard(OtherThread):
    def start(self, updateTimerMethod):
        worker = WorkerDashboard()
        worker.updateTimerSignal.connect(
            updateTimerMethod
        )
        super()._start(worker)

    def stop(self):
        super().stop()

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
