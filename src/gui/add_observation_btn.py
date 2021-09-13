# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar


class SammoAddObservationBtn(QObject):
    onClickObservationSignal = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QAction = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QAction(parent)
        self.button.setIcon(self.icon)
        self.button.setToolTip("New observation")
        self.button.triggered.connect(self.onClick)
        self.button.setEnabled(False)
        toolbar.addAction(self.button)

    def onNewSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def onClick(self):
        self.onClickObservationSignal.emit()

    @property
    def icon(self):
        d = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(os.path.dirname(d))
        return QIcon(os.path.join(root, "images", "observation.png"))
