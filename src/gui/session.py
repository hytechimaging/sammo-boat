# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtCore import QDir, pyqtSignal, QObject


class SammoActionSession(QObject):
    create = pyqtSignal(str)

    def __init__(self, parent, toolbar):
        super().__init__()
        self.action = None
        self.initGui(parent, toolbar)

    def initGui(self, parent, toolbar):
        self.action = QAction("Session", parent)
        self.action.triggered.connect(self.run)
        toolbar.addAction(self.action)

    def unload(self):
        del self.action

    def run(self):
        workingDirectory = QFileDialog.getExistingDirectory(
            None, "Select a working directory", QDir.currentPath()
        )
        if not workingDirectory:
            # no directory selected
            return

        self.create.emit(workingDirectory)
