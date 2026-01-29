# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt import QtCore
from qgis.gui import QgisInterface
from qgis.core import QgsVectorLayer
from typing import Optional, Callable
from qgis.PyQt.QtWidgets import (
    QFrame,
    QAction,
    QDialog,
    QToolBar,
    QLineEdit,
    QTableView,
)

from ..core import utils
from ..core.database import SIGHTINGS_TABLE, ENVIRONMENT_TABLE, FOLLOWERS_TABLE


class SammoAttributeTable:
    @staticmethod
    def toolbar(table: QDialog) -> QToolBar:
        return table.findChild(QToolBar, "mToolbar")

    @staticmethod
    def refresh(
        table: QDialog,
        layerName: str,
        filterExpr: str = "True",
        focus: bool = True,
    ) -> None:
        table.findChild(QLineEdit, "mFilterQuery").setValue(filterExpr)
        table.findChild(QAction, "mActionApplyFilter").trigger()
        table.findChild(QAction, "mActionReload").trigger()

        view = table.findChild(QTableView, "mTableView")
        view.resizeColumnsToContents()
        if layerName.casefold() == SIGHTINGS_TABLE:
            for i in range(view.model().columnCount()):
                if view.model().headerData(i, 1) == "species":
                    index = view.model().index(0, i)
        elif layerName.casefold() == ENVIRONMENT_TABLE:
            for i in range(view.model().columnCount()):
                if view.model().headerData(i, 1) == "routeType":
                    index = view.model().index(0, i)
        elif layerName.casefold() == FOLLOWERS_TABLE:
            for i in range(view.model().columnCount()):
                if view.model().headerData(i, 1) == "species":
                    index = view.model().index(view.model().rowCount() - 1, i)

        if not focus:
            return

        view.selectionModel().setCurrentIndex(
            index,
            QtCore.QItemSelectionModel.ClearAndSelect
            | QtCore.QItemSelectionModel.Rows,
        )

    @staticmethod
    def attributeTable(
        iface: QgisInterface,
        layer: QgsVectorLayer,
        filterExpr: str = "True",
        sortExpr: str = '"dateTime"',
        validate_callback: Optional[Callable] = None,
    ) -> QDialog:
        # hide some columns
        hiddens = [
            "copy",
            "fid",
            "endDateTime",
            "soundFile",
            "soundStart",
            "soundEnd",
            "survey",
            "cycle",
            "session",
            "shipName",
            "computer",
            "transect",
            "strateType",
            "length",
            "plateformHeight",
            "observer",
            "_effortGroup",
            "_effortLeg",
        ]
        if layer.name().lower() != ENVIRONMENT_TABLE:
            hiddens += ["effortGroup", "effortLeg"]
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name in hiddens:
                column.hidden = True
        config.setColumns(columns)
        config.setSortExpression(sortExpr)
        config.setSortOrder(QtCore.Qt.DescendingOrder)
        layer.setAttributeTableConfig(config)

        # init attribute table
        table = iface.showAttributeTable(layer, filterExpr)

        # hide some items
        last = table.layout().rowCount() - 1
        layout = table.layout().itemAtPosition(last, 0).itemAt(0)
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        layout = table.findChild(QFrame, "mUpdateExpressionBox").layout()
        for idx in range(layout.count()):
            layout.itemAt(idx).widget().hide()

        SammoAttributeTable.toolbar(table).hide()
        if validate_callback:
            toolbar = QToolBar()
            validateAction = QAction(table)
            validateAction.setObjectName("Follower_validate")
            validateAction.triggered.connect(
                lambda x: validate_callback(table)
            )
            validateAction.setIcon(utils.icon("pen_valid.png"))
            validateAction.setToolTip("Validate (all or current selection)")
            validateAction.setText("Validate (all or current selection)")
            toolbar.addAction(validateAction)
            table.layout().addWidget(toolbar, 0, 0)
            table.setModal(True)

        # update table view
        view = table.findChild(QTableView, "mTableView")
        view.horizontalHeader().setStretchLastSection(True)
        view.model().rowsInserted.connect(
            lambda: QtCore.QTimer.singleShot(0, view.scrollToTop)
        )

        return table
