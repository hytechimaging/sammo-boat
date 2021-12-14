# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QToolBar,
    QFileDialog,
)

from qgis.core import QgsVectorFileWriter

from ..core import utils
from ..core.session import SammoSession


class SammoExportAction(QDialog):
    def __init__(
        self, parent: QObject, toolbar: QToolBar, session: SammoSession
    ):
        super().__init__()
        uic.loadUi(Path(__file__).parent / "ui/export.ui", self)
        self.action: QAction = None
        self.session = session
        self.initGui(parent, toolbar)

        self.searchDirButton.clicked.connect(self.updateSaveFolder)
        self.exportButton.clicked.connect(self.export)

    def setEnabled(self, status):
        self.action.setEnabled(status)
        self.action.setChecked(False)

    def initGui(self, parent: QObject, toolbar: QToolBar) -> None:
        self.action = QAction(parent)
        self.action.triggered.connect(self.show)
        self.action.setIcon(utils.icon("export.png"))
        self.action.setToolTip("Export session as CSV")
        toolbar.addAction(self.action)

    def updateSaveFolder(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Dossier d'export",
            self.session.db.directory,
            options=QFileDialog.ShowDirsOnly,
        )
        self.saveFolderEdit.setText(path)

    def export(self):
        nb = len(self.session.allLayers)
        for i, layer in enumerate(self.session.allLayers):
            self.progressBar.setFormat(
                f"Export de la couche {layer.name()}, Total : %p%"
            )
            QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                (
                    Path(self.saveFolderEdit.text()) / f"{layer.name()}.csv"
                ).as_posix(),
                "utf-8",
                driverName="CSV",
                layerOptions=["GEOMETRY=AS_XY"],
            )
            self.progressBar.setValue(int(100 / nb * (i + 1)))
        self.close()
