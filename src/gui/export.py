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
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsVectorLayerJoinInfo,
    QgsCoordinateTransformContext,
)

from ..core import utils
from ..core.status import StatusCode
from ..core.session import SammoSession
from ..core.database import SIGHTINGS_TABLE, ENVIRONMENT_TABLE, FOLLOWERS_TABLE


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

    def applyEnvAttr(self):
        environmentLayer = self.session.environmentLayer
        # Sightings
        sightingsLayer = self.session.sightingsLayer
        sightingsLayer.startEditing()
        for feat in sightingsLayer.getFeatures():
            strDateTime = (
                feat["dateTime"].toPyDateTime().strftime("%Y-%m-%d %H:%M:%S")
            )
            request = QgsFeatureRequest().setFilterExpression(
                f"dateTime < to_datetime('{strDateTime}') "
                f"and status != '{StatusCode.display(StatusCode.END)}'"
            )
            request.addOrderBy("dateTime", False)
            for envFeat in environmentLayer.getFeatures(request):
                if feat["side"] == "L":
                    sightingsLayer.changeAttributeValue(
                        feat.id(),
                        sightingsLayer.fields().indexOf("observer"),
                        envFeat["left"],
                    )
                elif feat["side"] == "R":
                    sightingsLayer.changeAttributeValue(
                        feat.id(),
                        sightingsLayer.fields().indexOf("observer"),
                        envFeat["right"],
                    )
                elif feat["side"] == "C":
                    sightingsLayer.changeAttributeValue(
                        feat.id(),
                        sightingsLayer.fields().indexOf("observer"),
                        envFeat["center"],
                    )
                sightingsLayer.changeAttributeValue(
                    feat.id(),
                    sightingsLayer.fields().indexOf("_effortGroup"),
                    envFeat["_effortGroup"],
                )
                sightingsLayer.changeAttributeValue(
                    feat.id(),
                    sightingsLayer.fields().indexOf("_effortLeg"),
                    envFeat["_effortLeg"],
                )
                break
        sightingsLayer.commitChanges()
        sightingsLayer.startEditing()

        # Followers
        followersLayer = self.session.followersLayer
        followersLayer.startEditing()
        for feat in followersLayer.getFeatures():
            strDateTime = (
                feat["dateTime"].toPyDateTime().strftime("%Y-%m-%d %H:%M:%S")
            )
            request = QgsFeatureRequest().setFilterExpression(
                f"dateTime < to_datetime('{strDateTime}') "
                f"and status != '{StatusCode.display(StatusCode.END)}'"
            )
            request.addOrderBy("dateTime", False)
            for envFeat in environmentLayer.getFeatures(request):
                followersLayer.changeAttributeValue(
                    feat.id(),
                    followersLayer.fields().indexOf("_effortGroup"),
                    envFeat["_effortGroup"],
                )
                break

        followersLayer.commitChanges()
        followersLayer.startEditing()

    def export(self) -> None:
        self.applyEnvAttr()
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
                field = QgsField("lon", QVariant.Double)
                layer.addExpressionField("x($geometry) ", field)
                field = QgsField("lat", QVariant.Double)
                layer.addExpressionField("y($geometry) ", field)

            if layer.name().lower() in [
                SIGHTINGS_TABLE,
                ENVIRONMENT_TABLE,
                FOLLOWERS_TABLE,
            ]:
                field = QgsField("effortGroup", QVariant.String)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_G', _effortGroup)",
                    field,
                )
                field = QgsField("effortLeg", QVariant.String)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_L', _effortLeg)",
                    field,
                )

            if layer.name().lower() in [SIGHTINGS_TABLE, ENVIRONMENT_TABLE]:
                field = QgsField("date", QVariant.Date)
                layer.addExpressionField('to_date("dateTime")', field)
                field = QgsField("hhmmss", QVariant.Time)
                layer.addExpressionField('to_time("dateTime")', field)

            elif layer.name().lower() == FOLLOWERS_TABLE:
                field = QgsField("focalId", QVariant.String)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_F', _focalId)",
                    field,
                )

            # Add joined fields
            if layer.name().lower() in [SIGHTINGS_TABLE, FOLLOWERS_TABLE]:
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
                if field.name()
                not in [
                    "sightNum",
                    "validated",
                    "plateformId",
                    "_effortLeg",
                    "_effortGroup",
                    "_focalId",
                ]
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
            [
                "name_latin",
                "name_eng",
                "group_eng",
                "family_eng",
                "taxon_eng",
                "name_fr",
                "group_fr",
                "family_fr",
                "taxon_fr"
            ]
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
