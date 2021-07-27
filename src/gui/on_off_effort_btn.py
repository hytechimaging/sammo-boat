# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QPushButton, QToolBar
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsVectorLayer, QgsFeature


class SammoOnOffEffortBtn(QObject):
    onChangeEffortStatusSignal = pyqtSignal(bool)
    onAddFeatureToEnvironmentTableSignal = pyqtSignal(QgsFeature)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Effort")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        toolbar.addWidget(self.button)

    def onCreateSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def onClick(self):
        if self.button.isChecked():
            self.onChangeEffortStatusSignal.emit(True)
        else:
            self.onChangeEffortStatusSignal.emit(False)

    def openFeatureForm(self, iface, table: QgsVectorLayer, feat: QgsFeature):
        if iface.openFeatureForm(table, feat):
            self.onAddFeatureToEnvironmentTableSignal.emit(feat)

    def isChecked(self) -> bool:
        return self.button.isChecked()
