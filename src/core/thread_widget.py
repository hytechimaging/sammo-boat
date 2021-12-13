# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from time import sleep
from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal


class WorkerWidget(WorkerForOtherThread):
    timer_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lines = None

    def _toDoInsideLoop(self):
        sleep(2)
        self.timer_signal.emit()

    def _onStart(self):
        pass


class ThreadWidget(OtherThread):
    def __init__(self, timerMethod):
        super().__init__()
        self._timerMethod = timerMethod

    def start(self):
        worker = WorkerWidget()
        worker.timer_signal.connect(self._timerMethod)
        super()._start(worker)
