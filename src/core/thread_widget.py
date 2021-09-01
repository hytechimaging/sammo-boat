# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from datetime import datetime


class WorkerWidget(WorkerForOtherThread):
    timer_1sec_signal = pyqtSignal()
    timer_500msec_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lines = None

    def _toDoInsideLoop(self):
        sleep(0.5)
        self.timer_500msec_signal.emit()
        sleep(0.5)
        self.timer_500msec_signal.emit()
        self.timer_1sec_signal.emit()

    def _onStart(self):
        pass


class ThreadWidget(OtherThread):
    def __init__(self, timerMethod_1sec, timerMethod_500msec):
        super().__init__()
        self._timerMethod_1sec = timerMethod_1sec
        self._timerMethod_500msec = timerMethod_500msec

    def start(self):
        worker = WorkerWidget()
        worker.timer_1sec_signal.connect(self._timerMethod_1sec)
        worker.timer_500msec_signal.connect(self._timerMethod_500msec)
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
