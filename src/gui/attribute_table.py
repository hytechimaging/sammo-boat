# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QFrame, QTableView, QAction, QToolBar


class SammoAttributeTable:
    @staticmethod
    def toolbar(table):
        return table.findChild(QToolBar, "mToolbar")

    @staticmethod
    def refresh(table):
        table.findChild(QAction, "mActionReload").trigger()
        table.findChild(QAction, "mActionApplyFilter").trigger()

        table.findChild(QTableView).resizeColumnsToContents()

    @staticmethod
    def attributeTable(iface, layer, filter_expr=""):
        # hide some columns
        hiddens = ["copy", "fid", "soundFile", "soundStart", "soundEnd"]
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name in hiddens:
                column.hidden = True
        config.setColumns(columns)
        layer.setAttributeTableConfig(config)

        # init attribute table
        table = iface.showAttributeTable(layer, filter_expr)

        # hide some items
        last = table.layout().rowCount() - 1
        layout = table.layout().itemAtPosition(last, 0).itemAt(0)
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        layout = table.findChild(QFrame, "mUpdateExpressionBox").layout()
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        SammoAttributeTable.toolbar(table).hide()

        # update table view
        view = table.findChild(QTableView)
        view.horizontalHeader().setStretchLastSection(True)
        view.model().rowsInserted.connect(
            lambda: QtCore.QTimer.singleShot(0, view.scrollToBottom)
        )

        return table
