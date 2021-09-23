# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsVectorLayer, QgsFeature
from qgis.PyQt.QtWidgets import QPushButton, QToolBar


class SammoChangeEnvironmentBtn(QObject):
    onClickChangeEnvironmentBtnSignal = pyqtSignal(bool)
    onAddFeatureToEnvironmentTableSignal = pyqtSignal(QgsFeature)

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

    def unload(self):
        del self.button

    def onClick(self):
        self.onClickChangeEnvironmentBtnSignal.emit(False)

    def openFeatureForm(self, iface, table: QgsVectorLayer, feat: QgsFeature):
        if iface.openFeatureForm(table, feat):
            self.onAddFeatureToEnvironmentTableSignal.emit(feat)
        else:
            self.button.setChecked(False)

    def isChecked(self) -> bool:
        return self.button.isChecked()

