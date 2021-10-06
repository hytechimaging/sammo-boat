# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsVectorLayer, QgsFeature
from qgis.PyQt.QtWidgets import QPushButton, QToolBar


class SammoEnvironmentAction(QObject):
    triggered = pyqtSignal()
    add = pyqtSignal(QgsFeature)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QIcon = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Change environment")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(False)
        toolbar.addWidget(self.button)

    def onChangeEffortStatus(self, effortStatus: bool):
        self.button.setEnabled(effortStatus)

    def setEnabled(self, status: bool) -> None:
        self.button.setEnabled(status)

    def unload(self):
        del self.button

    def onClick(self):
        self.triggered.emit()

    def openFeatureForm(
        self, iface, table: QgsVectorLayer, feat: QgsFeature
    ) -> bool:
        if iface.openFeatureForm(table, feat):
            self.add.emit(feat)
            return True
        else:
            return False
