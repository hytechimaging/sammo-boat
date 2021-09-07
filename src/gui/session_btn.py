# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QDir, pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QToolBar


class SammoActionSession(QObject):
    createSignal = pyqtSignal(str)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.triggered.connect(self.run)
        self.action.setIcon(self.icon)
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

        self.createSignal.emit(workingDirectory)

    @property
    def icon(self):
        d = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(os.path.dirname(d))
        return QIcon(os.path.join(root, "images", "session.png"))
