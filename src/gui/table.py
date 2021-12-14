# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QFrame,
    QLabel,
    QDockWidget,
)

from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/table.ui")
)


class TableWidget(QFrame, FORM_CLASS):
    def __init__(self, iface, environmentLayer, sightingLayer):
        super().__init__()
        self.setupUi(self)

        self.tables = {}
        self.tables[
            environmentLayer.name()
        ] = SammoAttributeTable.attributeTable(iface, environmentLayer)
        self.tables[sightingLayer.name()] = SammoAttributeTable.attributeTable(
            iface, sightingLayer
        )
        self.verticalLayout.addWidget(self.tables[environmentLayer.name()])
        self.verticalLayout.addWidget(QLabel("Sightings"))
        self.verticalLayout.addWidget(self.tables[sightingLayer.name()])


class SammoTableDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Environment", iface.mainWindow())
        self.setObjectName("Sammo Tables")
        self.iface = iface
        self._widget = None

    def init(self, environmentLayer, sightingsLayer):
        self.iface.removeDockWidget(self)

        self._widget = TableWidget(
            self.iface, environmentLayer, sightingsLayer
        )
        self.setWidget(self._widget)
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self)

    def refresh(self, layer):
        table = self._widget.tables[layer.name()]
        SammoAttributeTable.refresh(table)
