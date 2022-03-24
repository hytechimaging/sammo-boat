# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.core import QgsSettings
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog, QTableView

from ..core import utils
from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/follower.ui")
)


class SammoFollowersAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.setIcon(utils.icon("seabird.png"))
        self.action.setToolTip("New follower")
        self.action.triggered.connect(self.onClick)
        self.action.setEnabled(False)
        toolbar.addAction(self.action)

    def unload(self):
        del self.action

    def onClick(self):
        self.triggered.emit()


class SammoFollowersTable(QDialog, FORM_CLASS):
    def __init__(self, iface, geom, followerLayer):
        super().__init__()
        self.iface = iface
        self.geom = geom

        self.setupUi(self)
        self.addButton.setIcon(utils.icon("plus.png"))

        lastView = int(QgsSettings().value("qgis/attributeTableLastView", 0))
        QgsSettings().setValue("qgis/attributeTableLastView", 0)

        # the same datetime is used for all followers added in this session
        self.datetime = utils.now()
        filterExpr = (
            f"epoch(\"dateTime\") = epoch(to_datetime('{self.datetime}'))"
        )
        sortExpr = "fid"
        self.table = SammoAttributeTable.attributeTable(
            iface, followerLayer, filterExpr, sortExpr
        )
        QgsSettings().setValue("qgis/attributeTableLastView", lastView)

        self.verticalLayout.addWidget(self.table)

    def rowCount(self):
        return (
            self.table.findChild(QTableView, "mTableView").model().rowCount()
        )

    def show(self):
        super().show()
        self.refresh()

    def close(self):
        self.table.close()
        super().close()

    def refresh(self):
        SammoAttributeTable.refresh(self.table, "Followers")
