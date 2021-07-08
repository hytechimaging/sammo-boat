# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from ..core.session import SammoSession


class SammoActionSession:
    def __init__(self, mainWindow, toolBar, session):
        self.mainWindow = mainWindow
        self.action = None
        self.session = session
        self.toolBar = toolBar

    def initGui(self):
        self.action = QAction("Session", self.mainWindow)
        self.action.triggered.connect(self.run)
        self.toolBar.addAction(self.action)

    def unload(self):
        del self.action

    def run(self):
        workingDirectory = QFileDialog.getExistingDirectory(
            None, "Select a working directory", QDir.currentPath()
        )
        if not workingDirectory:
            # no directory selected
            return

        if not SammoSession.isDataBaseAvailable(workingDirectory):
            # No geopackage DB in this directory
            self.session.createEmptyDataBase(workingDirectory)

        self.session.directoryPath = workingDirectory
