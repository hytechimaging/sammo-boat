# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal


class WorkerWidget(WorkerForOtherThread):
    timer_500msec_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lines = None

    def _toDoInsideLoop(self):
        sleep(0.5)
        self.timer_500msec_signal.emit()

    def _onStart(self):
        pass


class ThreadWidget(OtherThread):
    def __init__(self, timerMethod_500msec):
        super().__init__()
        self._timerMethod_500msec = timerMethod_500msec

    def start(self):
        worker = WorkerWidget()
        worker.timer_500msec_signal.connect(self._timerMethod_500msec)
        super()._start(worker)
