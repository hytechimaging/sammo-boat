# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QPushButton, QToolBar
from qgis.PyQt.QtCore import pyqtSignal, QObject


class StopThreadsBtn(QObject):
    onStopThreadsSignal = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QPushButton = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QPushButton(parent)
        self.button.setText("Stop threads")
        self.button.clicked.connect(self.onClick)
        self.button.setEnabled(True)
        toolbar.addWidget(self.button)

    def unload(self):
        del self.button

    def onClick(self):
        self.onStopThreadsSignal.emit()
