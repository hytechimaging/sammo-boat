# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.core import QgsSettings
from qgis.PyQt.QtGui import QKeyEvent
from qgis.PyQt.QtCore import Qt, QSize, QEvent
from qgis.PyQt.QtWidgets import (
    QFrame,
    QLabel,
    QWidget,
    QSplitter,
    QDockWidget,
    QVBoxLayout,
    QDialog,
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
        self.tables[environmentLayer.name()].setMinimumSize(QSize(10, 10))
        self.tables[environmentLayer.name()].installEventFilter(self)
        self.tables[sightingLayer.name()] = SammoAttributeTable.attributeTable(
            iface, sightingLayer
        )
        self.tables[sightingLayer.name()].setMinimumSize(QSize(10, 10))
        self.tables[sightingLayer.name()].installEventFilter(self)

        widget1 = QWidget()
        verticalLayout1 = QVBoxLayout()
        originDlg = self.tables[environmentLayer.name()].parent()
        self.tables[environmentLayer.name()].setParent(widget1)
        verticalLayout1.addWidget(self.tables[environmentLayer.name()])
        if originDlg:  # version < 3.28 compatibility
            originDlg.hide()
        widget1.setLayout(verticalLayout1)
        widget2 = QWidget()
        verticalLayout2 = QVBoxLayout()
        verticalLayout2.addWidget(QLabel("Sightings"))
        originDlg = self.tables[sightingLayer.name()].parent()
        self.tables[sightingLayer.name()].setParent(widget2)
        verticalLayout2.addWidget(self.tables[sightingLayer.name()])
        if originDlg:  # version < 3.28 compatibility
            originDlg.hide()
        widget2.setLayout(verticalLayout2)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(widget1)
        splitter.addWidget(widget2)
        self.verticalLayout.addWidget(splitter)

    def eventFilter(self, obj, event):
        if type(obj) == QDialog:
            if type(event) == QKeyEvent:
                if event.key() == Qt.Key_Escape:
                    event.ignore()
                    return True
            if event.type() == QEvent.Close:
                event.ignore()
                return True
        return super().eventFilter(obj, event)


class SammoTableDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Environment", iface.mainWindow())
        self.setObjectName("Sammo Tables")
        self.iface = iface
        self._widget = None

    def init(self, environmentLayer, sightingsLayer):
        lastView = int(QgsSettings().value("qgis/attributeTableLastView", 0))
        QgsSettings().setValue("qgis/attributeTableLastView", 0)

        self.clean()
        self._widget = TableWidget(
            self.iface, environmentLayer, sightingsLayer
        )
        self.setWidget(self._widget)
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self)
        self.iface.mainWindow().setCorner(
            Qt.BottomLeftCorner, Qt.BottomDockWidgetArea
        )
        self.iface.mainWindow().setCorner(
            Qt.BottomRightCorner, Qt.BottomDockWidgetArea
        )
        self.refresh(environmentLayer)
        self.refresh(sightingsLayer)
        QgsSettings().setValue("qgis/attributeTableLastView", lastView)

    def unload(self):
        self.clean()

    def refresh(self, layer, filterExpr="True"):
        table = self._widget.tables[layer.name()]
        SammoAttributeTable.refresh(table, layer.name(), filterExpr)

    def removeTable(self, name):
        if name in self._widget.tables:
            self._widget.tables[name].accept()
            self._widget.tables.pop(name, None)

    def clean(self):
        if self._widget:
            tableKeys = [k for k in self._widget.tables.keys()]
            for name in tableKeys:
                self.removeTable(name)
        self.iface.removeDockWidget(self)
        self.iface.mainWindow().setCorner(
            Qt.BottomLeftCorner, Qt.LeftDockWidgetArea
        )
        self.iface.mainWindow().setCorner(
            Qt.BottomRightCorner, Qt.RightDockWidgetArea
        )
