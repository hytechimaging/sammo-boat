# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QMessageBox, QPushButton
from qgis.core import QgsVectorLayerUtils

from ..core.database import SammoDataBase


class SammoActionOnOffEffort:
    def __init__(self, iface, toolBar, session):
        self.iface = iface
        self.mainWindow = self.iface.mainWindow()
        self.action = None
        self.session = session
        self.toolBar = toolBar
        self.button = None

    def initGui(self):
        self.button = QPushButton(self.mainWindow)
        self.button.setText("Effort")
        self.button.clicked.connect(self.run)
        self.button.setEnabled(False)
        self.toolBar.addWidget(self.button)

    def onCreateSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

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

        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()
        if self.iface.openFeatureForm(table, feat):
            table.addFeature(feat)
            table.commitChanges()

