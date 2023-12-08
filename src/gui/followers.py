# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.core import QgsSettings
from qgis.PyQt.QtGui import QKeyEvent
from qgis.PyQt.QtCore import QObject, Qt, QEvent
from qgis.PyQt.QtWidgets import (
    QMenu,
    QAction,
    QDialog,
    QToolBar,
    QTableView,
    QToolButton,
)

from ..core import utils
from .attribute_table import SammoAttributeTable

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/follower.ui")
)


class SammoFollowersAction(QObject):
    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QToolButton(parent)
        self.action.setPopupMode(QToolButton.MenuButtonPopup)
        self.action.setToolButtonStyle(Qt.ToolButtonIconOnly)
        menu = QMenu()

        self.follower = QAction(parent)
        self.follower.setIcon(utils.icon("seabird.png"))
        self.follower.setText("New follower")
        self.follower.setToolTip("New follower")
        menu.addAction(self.follower)
        self.followerTable = QAction(parent)
        self.followerTable.setIcon(utils.icon("pen.png"))
        self.followerTable.setText("Open followers table")
        self.followerTable.setToolTip("Followers table")
        menu.addAction(self.followerTable)
        self.action.setMenu(menu)
        self.action.setDefaultAction(self.follower)
        self.action.setEnabled(False)
        toolbar.addWidget(self.action)

    def unload(self):
        del self.action


class SammoFollowersTable(QDialog, FORM_CLASS):
    def __init__(self, iface, geom, followerLayer):
        super().__init__()
        self.iface = iface
        self.geom = geom

        self.setupUi(self)
        self.addButton.setIcon(utils.icon("plus.png"))

        lastView = int(QgsSettings().value("qgis/attributeTableLastView", 0))
        QgsSettings().setValue("qgis/attributeTableLastView", 0)

        if not followerLayer.featureCount():
            self.focalId = 1
        else:
            self.focalId = (
                followerLayer.maximumValue(
                    followerLayer.fields().indexOf("_focalId")
                )
                + 1
            )

        # the same datetime is used for all followers added in this session
        self.datetime = utils.now()
        filterExpr = (
            f"epoch(\"dateTime\") = epoch(to_datetime('{self.datetime}'))"
        )
        sortExpr = "fid"
        self.table = SammoAttributeTable.attributeTable(
            iface, followerLayer, filterExpr, sortExpr
        )
        originDlg = self.table.parent()
        self.table.installEventFilter(self)
        QgsSettings().setValue("qgis/attributeTableLastView", lastView)

        self.table.setParent(self)
        self.verticalLayout.addWidget(self.table)
        originDlg.hide()

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
        filterExpr = (
            f"epoch(\"dateTime\") = epoch(to_datetime('{self.datetime}'))"
        )
        SammoAttributeTable.refresh(self.table, "Followers", filterExpr)

    def eventFilter(self, obj, event):
        if type(event) is QKeyEvent:
            if event.key() == Qt.Key_Escape:
                event.ignore()
                return True
        if event.type() == QEvent.Close:
            event.ignore()
            return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.accept()
        else:
            super().keyPressEvent(event)
