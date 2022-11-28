# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QObject, QVariant
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QToolBar,
    QFileDialog,
)

from qgis.core import (
    QgsField,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsVectorLayerJoinInfo,
    QgsCoordinateTransformContext,
)

from ..core import utils
from ..core.session import SammoSession


class SammoExportAction(QDialog):
    def __init__(
        self, parent: QObject, toolbar: QToolBar, session: SammoSession
    ) -> None:
        super().__init__()
        uic.loadUi(Path(__file__).parent / "ui/export.ui", self)
        self.action: QAction = None
        self.session = session
        self.initGui(parent, toolbar)

        self.searchDirButton.clicked.connect(self.updateSaveFolder)
        self.cancelButton.clicked.connect(self.close)
        self.exportButton.clicked.connect(self.export)
        self.exportButton.setEnabled(False)

    def setEnabled(self, status: bool) -> None:
        self.action.setEnabled(status)
        self.action.setChecked(False)

    def initGui(self, parent: QObject, toolbar: QToolBar) -> None:
        self.action = QAction(parent)
        self.action.triggered.connect(self.show)
        self.action.setIcon(utils.icon("export.png"))
        self.action.setToolTip("Export session")
        toolbar.addAction(self.action)

    def updateSaveFolder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Export folder",
            self.session.db.directory,
            options=QFileDialog.ShowDirsOnly,
        )
        if path:
            self.saveFolderEdit.setText(path)
            self.exportButton.setEnabled(True)

    def export(self) -> None:
        driver = self.driverComboBox.currentText()
        if driver not in ["CSV", "GPKG"]:
            self.progressBar.setFormat("Unknown driver: aborting export")
            return

        nb = len(self.session.allLayers)
        for i, layer in enumerate(self.session.allLayers):
            self.progressBar.setFormat(
                f"Export layer {layer.name()}, Total : %p%"
            )

            # Export is done from copy to avoid bug with join field, due to
            # the table dock.
            layer = QgsVectorLayer(layer.source(), layer.name())

            # Add Lon/Lat field
            if layer.geometryType() == QgsWkbTypes.PointGeometry:
                field = QgsField("lat", QVariant.Double)
                layer.addExpressionField("x($geometry) ", field)
                field = QgsField("lon", QVariant.Double)
                layer.addExpressionField("y($geometry) ", field)

            # Add joined fields
            if layer.name() == self.session.sightingsLayer.name():
                joinLayer = QgsVectorLayer(
                    self.session.speciesLayer.source(),
                    self.session.speciesLayer.name(),
                )  # keepped alive until export is done
                layer.addJoin(self.sightingsLayerJoinInfo(joinLayer))

            elif layer.name() == self.session.environmentLayer.name():
                joinLayer = QgsVectorLayer(
                    self.session.observersLayer.source(),
                    self.session.observersLayer.name(),
                )  # keepped alive until export is done
                layer.addJoin(
                    self.environmentLayerJoinObserverInfo(joinLayer, "left")
                )
                layer.addJoin(
                    self.environmentLayerJoinObserverInfo(joinLayer, "rigth")
                )
                layer.addJoin(
                    self.environmentLayerJoinObserverInfo(joinLayer, "center")
                )
                joinLayer = QgsVectorLayer(
                    self.session.plateformLayer.source(),
                    self.session.plateformLayer.name(),
                )
                layer.addJoin(
                    self.environmentLayerJoinPlateformInfo(joinLayer)
                )

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver
            options.attributes = [
                layer.fields().indexOf(field.name())
                for field in layer.fields()
                if field.name() not in ["validated", "plateformId"]
            ]
            QgsVectorFileWriter.writeAsVectorFormatV2(
                layer,
                (
                    Path(self.saveFolderEdit.text())
                    / f"{layer.name()}.{driver.lower()}"
                ).as_posix(),
                QgsCoordinateTransformContext(),
                options,
            )
            self.progressBar.setValue(int(100 / nb * (i + 1)))
        self.close()

    def sightingsLayerJoinInfo(self, layer: QgsVectorLayer) -> None:
        joinInfo = QgsVectorLayerJoinInfo()
        joinInfo.setJoinLayer(layer)
        joinInfo.setJoinFieldName("species")
        joinInfo.setTargetFieldName("species")
        joinInfo.setPrefix("species_")
        joinInfo.setJoinFieldNamesSubset(
            ["commonName", "latinName", "groupName", "family", "taxon"]
        )
        return joinInfo

    def environmentLayerJoinObserverInfo(
        self, layer: QgsVectorLayer, side: str
    ) -> None:
        joinInfo = QgsVectorLayerJoinInfo()
        joinInfo.setJoinLayer(layer)
        joinInfo.setJoinFieldName("observer")
        joinInfo.setTargetFieldName(side)
        joinInfo.setPrefix(f"{side}_")
        joinInfo.setJoinFieldNamesSubset(
            ["firstName", "lastName", "organization"]
        )
        return joinInfo

    def environmentLayerJoinPlateformInfo(self, layer: QgsVectorLayer) -> None:
        joinInfo = QgsVectorLayerJoinInfo()
        joinInfo.setJoinLayer(layer)
        joinInfo.setJoinFieldName("fid")
        joinInfo.setTargetFieldName("plateformId")
        joinInfo.setPrefix("")
        joinInfo.setJoinFieldNamesSubset(["plateform", "plateformHeight"])
        return joinInfo
