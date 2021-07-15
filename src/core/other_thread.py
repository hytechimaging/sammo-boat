# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtCore import QThread, QObject, pyqtSignal
from .debug import Debug


class WorkerForOtherThread(QObject):
    finishedSignal = pyqtSignal()
    logSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._isNeedToStop = False

    def run(self):
        self._lines = self._onStart()

        while not self._isNeedToStop:
            self._toDoInsideLoop()

        self.finishedSignal.emit()

    @abstractmethod
    def _toDoInsideLoop(self):
        pass

    @abstractmethod
    def _onStart(self):
        pass

    def _log(self, msg: str):
        self.logSignal.emit(msg)

    def stop(self):
        self._isNeedToStop = True


class OtherThread:
    def start(self, worker: WorkerForOtherThread):
        self.thread = QThread()
        self.worker = worker
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finishedSignal.connect(self.thread.quit)
        self.worker.finishedSignal.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.logSignal.connect(self.log)

        self.thread.start()

    def stop(self):
        self.worker.stop()

    def log(self, msg: str):
        Debug.log(__name__ + " - " + msg)
