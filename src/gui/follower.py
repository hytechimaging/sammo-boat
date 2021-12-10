# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog

from ..core import icon
from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/follower.ui")
)


class SammoFollowerAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.setIcon(icon("seabird.png"))
        self.action.setToolTip("New follower")
        self.action.triggered.connect(self.onClick)
        self.action.setEnabled(False)
        toolbar.addAction(self.action)

    def unload(self):
        del self.action

    def onClick(self):
        self.triggered.emit()


class SammoFollowerTable(QDialog, FORM_CLASS):
    def __init__(self, iface, followerLayer):
        super().__init__()
        self.iface = iface

        self.setupUi(self)
        self.addButton.setIcon(icon("plus.png"))

        # the same datetime is used for all followers added in this session
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filter_expr = (
            f"epoch(\"dateTime\") = epoch(to_datetime('{self.datetime}'))"
        )
        self.table = SammoAttributeTable.attributeTable(
            iface, followerLayer, filter_expr
        )

        self.verticalLayout.addWidget(self.table)

    def show(self):
        super().show()
        self.refresh()

    def refresh(self):
        SammoAttributeTable.refresh(self.table)
