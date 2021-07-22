# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QPushButton, QToolBar


class AddObservationBtn(QObject):
    onClickObservationSignal = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Observation")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(False)
        toolbar.addWidget(self.button)

    def onChangeEffortStatus(self, effortStatus: bool):
        # effortStatus = True means that an effort is in progress
        self.button.setEnabled(effortStatus)

    def unload(self):
        del self.button

    def onClick(self):
        self.onClickObservationSignal.emit()
