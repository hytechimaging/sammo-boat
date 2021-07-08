# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from ..core.session import SammoSession


class SammoActionSession:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.session = SammoSession()

    def initGui(self):
        self.action = QAction("Session", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        workingDirectory = QFileDialog.getExistingDirectory(
            None, "Select a working directory", QDir.currentPath()
        )
        if not workingDirectory:
            # no directory selected
            return

        if not self.session.isDataBaseAvailable(workingDirectory):
            # No geopackage DB in this directory
            self.session.createEmptyDataBase(workingDirectory)

        self.session.directoryPath = workingDirectory
