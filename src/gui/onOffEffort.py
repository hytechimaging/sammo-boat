# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QMessageBox, QAction
from qgis._core import QgsFeature

from ..core.session import SammoSession
from ..core.database import SammoDataBase


class SammoActionOnOffEffort:
    def __init__(self, iface, toolBar, session):
        self.iface = iface
        self.mainWindow = self.iface.mainWindow()
        self.action = None
        self.session = session
        self.toolBar = toolBar

    def initGui(self):
        self.action = QAction("Effort", self.mainWindow)
        self.action.triggered.connect(self.run)
        self.toolBar.addAction(self.action)

    def unload(self):
        del self.action

    def run(self):
        print("Effort button pressed")
        table = self.session.loadTable(SammoDataBase.ENVIRONMENT_TABLE_NAME)
        if not table.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the environment table "
            )
            return

        feat = QgsFeature();
        feat.setFields(table.fields())
        self.iface.openFeatureForm(table, feat)
