# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtWidgets import QMessageBox


class SammoActionSession:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Session", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        outputFolder = QFileDialog.getExistingDirectory(None, "Select a working directory",
                                                        QDir.currentPath())
        if not outputFolder: # no directory selected
            return

        print("Le répertoire sélectionné = " + outputFolder)
