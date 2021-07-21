# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QPushButton, QToolBar
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsVectorLayer, QgsFeature


class SammoActionOnOffEffort(QObject):
    onStartEffortSignal = pyqtSignal()
    onStopEffortSignal = pyqtSignal()
    onAddFeatureToEnvironmentTableSignal = pyqtSignal(QgsFeature)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Effort")
        self.button.clicked.connect(self.run)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        toolbar.addWidget(self.button)

    def onCreateSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def run(self):
        if self.button.isChecked():
            self.onStartEffortSignal.emit()
        else:
            self.onStopEffortSignal.emit()

    def OpenFeatureForm(self, iface, table: QgsVectorLayer, feat: QgsFeature):
        if iface.openFeatureForm(table, feat):
            self.onAddFeatureToEnvironmentTableSignal.emit(feat)
