# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar

from ..core import icon


class SammoEnvironmentAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.setIcon(icon("environment.png"))
        self.action.setToolTip("Update environment")
        self.action.triggered.connect(self.onClick)
        self.action.setEnabled(False)
        toolbar.addAction(self.action)

    def onChangeEffortStatus(self, effortStatus: bool):
        self.action.setEnabled(effortStatus)

    def setEnabled(self, status: bool) -> None:
        self.action.setEnabled(status)

    def unload(self):
        del self.action

    def onClick(self):
        self.triggered.emit()
