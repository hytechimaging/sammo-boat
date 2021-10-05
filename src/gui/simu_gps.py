# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QPushButton, QToolBar
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsVectorLayer, QgsFeature


class SammoSimuGpsAction(QObject):
    # the parameter value is true if GPS simulation is ON
    onChangeSimuGpsStatusSignal = pyqtSignal(bool)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Simu GPS")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        toolbar.addWidget(self.button)

    def onNewSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def onClick(self):
        self.onChangeSimuGpsStatusSignal.emit(self.button.isChecked())

    def isChecked(self) -> bool:
        return self.button.isChecked()

    def openFeatureForm(self, iface, table: QgsVectorLayer, feat: QgsFeature):
        if iface.openFeatureForm(table, feat):
            self.onAddFeatureToEnvironmentTableSignal.emit(feat)
