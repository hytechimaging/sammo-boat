# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"


from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from ..core.session import SammoSession


class SammoActionOnOffEffort:
    def __init__(self, iface, toolBar):
        self.iface = iface
        self.mainWindow = self.iface.mainWindow()
        self.action = None
        self.session = SammoSession()
        self.toolBar = toolBar

    def initGui(self):
        self.action = QAction("Effort", self.mainWindow)
        self.action.triggered.connect(self.run)
        self.toolBar.addAction(self.action)

    def unload(self):
        del self.action

    def run(self):
        print("Effort button pressed")
