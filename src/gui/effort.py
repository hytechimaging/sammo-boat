# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar

from ..core import icon


class SammoEffortAction(QObject):
    updateEffort = pyqtSignal(bool)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.action: QIcon = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)
        self.action.setChecked(False)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.setIcon(icon("effort.png"))
        self.action.setToolTip("Start/stop effort")
        self.action.triggered.connect(self.onClick)
        self.action.setEnabled(False)
        self.action.setCheckable(True)
        toolbar.addAction(self.action)

    def unload(self):
        del self.action

    def onClick(self):
        self.updateEffort.emit(self.action.isChecked())
