# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import QFrame, QLabel, QDockWidget, QTableView, QAction, QHeaderView, QToolBar

from qgis.core import QgsSettings

from ..core import pixmap
from ..core.thread_widget import ThreadWidget

from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/table.ui")
)


class TableWidget(QFrame, FORM_CLASS):
    def __init__(self, iface, environmentLayer, sightingLayer):
        super().__init__()
        self.setupUi(self)

        self.environmentTable = SammoAttributeTable.attributeTable(iface, environmentLayer)
        self.sightingTable = SammoAttributeTable.attributeTable(iface, sightingLayer)

        self.verticalLayout.addWidget(self.environmentTable)
        self.verticalLayout.addWidget(QLabel("Sightings"))
        self.verticalLayout.addWidget(self.sightingTable)


class TableDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Environment", iface.mainWindow())
        self.setObjectName("Sammo Tables")
        self.iface = iface
        self._widget = None

    def init(self, environmentLayer, sightingsLayer):
        self.iface.removeDockWidget(self)

        self._widget = TableWidget(self.iface, environmentLayer, sightingsLayer)
        self.setWidget(self._widget)
        self.iface.addDockWidget(
            Qt.BottomDockWidgetArea, self
        )

    def refresh(self, layer):
        table = self._widget.tables[layer.name()]
        TableWidget.refresh(table)
