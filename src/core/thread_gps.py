# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from time import sleep


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    isNeedToContinue = True

    def run(self):
        """Long-running task."""
        i = 1
        while self.isNeedToContinue:
            sleep(1)
            self.progress.emit(i)
            i = i + 1

        self.finished.emit()

    def stop(self):
        self.isNeedToContinue = False

class ThreadGps:
    def run(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)

        self.thread.start()

    def stop(self):
        self.worker.stop()

    def reportProgress(self, u: int):
        print("Progress : " + str(u))
