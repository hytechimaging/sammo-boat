# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtCore import QThread, QObject, pyqtSignal
from .logger import Logger


class WorkerForOtherThread(QObject):
    finishedSignal = pyqtSignal()
    logSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._isNeedToStop = False

    def run(self):
        self._onStart()

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


class OtherThread(QObject):
    def __init__(self):
        super().__init__()
        self.isProceeding: bool = False
        self._worker: WorkerForOtherThread = None

    def _start(self, worker: WorkerForOtherThread):
        self._thread = QThread()
        self._worker = worker
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finishedSignal.connect(self._thread.quit)
        self._worker.finishedSignal.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.logSignal.connect(self.log)

        self._thread.start()
        self.isProceeding = True

    def stop(self):
        self._worker.stop()
        self._worker = None
        self.isProceeding = False

    def log(self, msg: str):
        Logger.log("{} - {}".format(__name__, msg))
