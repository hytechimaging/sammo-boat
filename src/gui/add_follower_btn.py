# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QPushButton, QToolBar
from qgis.core import QgsVectorLayer, QgsFeature


class SammoAddFollowerBtn(QObject):
    onClickAddFollowerSignal = pyqtSignal()
    onAddFeatureToFollowerTableSignal = pyqtSignal(QgsFeature)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Add follower")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(False)
        toolbar.addWidget(self.button)

    def onCreateSession(self):
        # effortStatus = True means that an effort is in progress
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def onClick(self):
        self.onClickAddFollowerSignal.emit()

    def openFeatureForm(self, iface, table: QgsVectorLayer, feat: QgsFeature):
        if iface.openFeatureForm(table, feat):
            self.onAddFeatureToFollowerTableSignal.emit(feat)
