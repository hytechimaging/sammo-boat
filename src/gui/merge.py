# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog

from ..core import utils
from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/merge.ui")
)


class SammoMergeAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.setIcon(utils.icon("merge.png"))
        self.action.setToolTip("Merge projects")
        self.action.triggered.connect(self.onClick)
        toolbar.addAction(self.action)

    def unload(self):
        del self.action

    def onClick(self):
        self.triggered.emit()


class SammoMergeDialog(QDialog, FORM_CLASS):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ok.clicked.connect(self.merge)
        self.cancel.clicked.connect(self.close)

    def merge(self):
        pass
