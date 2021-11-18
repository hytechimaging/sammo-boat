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

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/table.ui")
)


class TableWidget(QFrame, FORM_CLASS):
    def __init__(self, iface, environmentLayer, sightingsLayer):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        self.tables = {}
        self.tables[environmentLayer.name()] = self._attributeTable(environmentLayer)
        self.tables[sightingsLayer.name()] = self._attributeTable(sightingsLayer)

        self.verticalLayout.addWidget(self.tables[environmentLayer.name()])
        self.verticalLayout.addWidget(self.tables[sightingsLayer.name()])

    @staticmethod
    def toolbar(table):
        return table.findChild(QToolBar, "mToolbar")

    @staticmethod
    def refresh(table):
        table.findChild(QAction, "mActionReload").trigger()
        table.findChild(QTableView).resizeColumnsToContents()

    def _attributeTable(self, layer):
        # hide some columns
        hiddens = ["fid", "soundFile", "soundStart", "soundEnd"]
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name in hiddens:
                column.hidden = True
        config.setColumns( columns )
        layer.setAttributeTableConfig( config )

        # init attribute table
        table = self.iface.showAttributeTable(layer)

        # hide some items
        last = table.layout().rowCount() - 1
        layout = table.layout().itemAtPosition(last, 0).itemAt(0)
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        layout = table.findChild(QFrame, "mUpdateExpressionBox").layout()
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        TableWidget.toolbar(table).hide()

        # update table view
        table.findChild(QTableView).horizontalHeader().setStretchLastSection(True)

        return table


class TableDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Sammo Tables", iface.mainWindow())
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
