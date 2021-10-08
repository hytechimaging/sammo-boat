# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar

from ..core import icon


class SammoObservationAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.button: QAction = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QAction(parent)
        self.button.setIcon(icon("observation.png"))
        self.button.setToolTip("New observation")
        self.button.triggered.connect(self.onClick)
        self.button.setEnabled(False)
        toolbar.addAction(self.button)

    def setEnabled(self, status):
        self.button.setEnabled(status)

    def unload(self):
        del self.button

    def onClick(self):
        self.triggered.emit()
