# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import QFrame, QLabel, QDockWidget

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
        self.verticalLayout.addWidget(self._attributeTable(environmentLayer))
        self.verticalLayout.addWidget(self._attributeTable(sightingsLayer))

    def _attributeTable(self, layer):
        table = self.iface.showAttributeTable(
            layer,
            """
            array_contains(
            array_reverse(
                array_slice(
                    aggregate(
                        @layer,
                        'array_agg',
                        "fid",
                        order_by:="fid"
                    ),
                    -3,
                    -1
                )
            ),
            "fid"
            )
            """,
        )

        last = table.layout().rowCount() - 1
        hbox = table.layout().itemAtPosition(last, 0).itemAt(0)
        hbox.itemAt(0).widget().hide()
        hbox.itemAt(1).widget().hide()
        hbox.itemAt(2).widget().hide()

        for child in table.children():
            if "mToolbar" in child.objectName():
                child.hide()

        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            print(column.name)
            if column.name == "fid":
                column.hidden = True
                break
        config.setColumns( columns )
        layer.setAttributeTableConfig( config )

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
