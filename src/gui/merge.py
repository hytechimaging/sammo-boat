# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, QObject, QDir
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog, QFileDialog

from ..core import utils
from ..core.session import SammoSession

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/merge.ui")
)


class SammoMergeAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status: bool) -> None:
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar) -> None:
        self.action = QAction(parent)
        self.action.setIcon(utils.icon("merge.png"))
        self.action.setToolTip("Merge projects")
        self.action.triggered.connect(self.onClick)
        toolbar.addAction(self.action)

    def unload(self) -> None:
        del self.action

    def onClick(self) -> None:
        self.triggered.emit()


class SammoMergeDialog(QDialog, FORM_CLASS):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ok.clicked.connect(self.merge)
        self.cancel.clicked.connect(self.close)
        self.sessionAButton.clicked.connect(self.sessionA)
        self.sessionBButton.clicked.connect(self.sessionB)
        self.sessionMergedButton.clicked.connect(self.sessionMerged)

    def sessionA(self) -> None:
        sessionA = QFileDialog.getExistingDirectory(
            None,
            "Session A",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionA:
            self.sessionADir.setText(sessionA)

    def sessionB(self) -> None:
        sessionB = QFileDialog.getExistingDirectory(
            None,
            "Session B",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionB:
            self.sessionBDir.setText(sessionB)

    def sessionMerged(self) -> None:
        sessionMerged = QFileDialog.getExistingDirectory(
            None,
            "Session merged",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionMerged:
            self.sessionMergedDir.setText(sessionMerged)

    def merge(self) -> None:
        SammoSession.merge(
            self.sessionADir.text(),
            self.sessionBDir.text(),
            self.sessionMergedDir.text(),
        )
        self.close()
