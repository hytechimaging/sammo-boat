# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QObject, QDateTime, QMetaType
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QToolBar,
    QFileDialog,
)

from qgis.core import (
    QgsField,
    QgsWkbTypes,
    QgsGeometry,
    QgsExpression,
    QgsVectorLayer,
    QgsGeometryUtils,
    QgsFeatureRequest,
    QgsVectorLayerUtils,
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
        self.action.triggered.connect(self.clean)
        self.action.setIcon(utils.icon("export.png"))
        self.action.setToolTip("Export session")
        toolbar.addAction(self.action)

    def clean(self):
        self.saveFolderEdit.setText("")
        self.driverComboBox.setCurrentIndex(0)
        self.progressBar.setFormat("%p%")
        self.progressBar.setValue(0)

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
        success = self.session.effortCheck(self.session.environmentLayer)
        if not success:
            self.progressBar.setFormat("Fix environnment endDateTime first")
            return
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
            if layer.name() in [FOLLOWERS_TABLE, SIGHTINGS_TABLE]:
                self.session.applyEnvAttr(self.session.environmentLayer, layer)

            # Add Lon/Lat field
            if layer.geometryType() == QgsWkbTypes.PointGeometry:
                field = QgsField("lon", QMetaType.Type.Double)
                layer.addExpressionField("x($geometry) ", field)
                field = QgsField("lat", QMetaType.Type.Double)
                layer.addExpressionField("y($geometry) ", field)
            if layer.geometryType() == QgsWkbTypes.LineGeometry:
                field = QgsField("wkt", QMetaType.Type.QString)
                layer.addExpressionField("geom_to_wkt($geometry) ", field)

            if layer.name().lower() in [
                SIGHTINGS_TABLE,
                ENVIRONMENT_TABLE,
                FOLLOWERS_TABLE,
            ]:
                field = QgsField("effortGroup", QMetaType.Type.QString)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_G', _effortGroup)",
                    field,
                )
                field = QgsField("effortLeg", QMetaType.Type.QString)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_L', _effortLeg)",
                    field,
                )
                field = QgsField("_effortId", QMetaType.Type.QString)
                layer.addExpressionField(
                    "to_string(_effortGroup) + '_' + to_string(_effortLeg)",
                    field,
                )

            if layer.name().lower() in [SIGHTINGS_TABLE, ENVIRONMENT_TABLE]:
                field = QgsField("date", QMetaType.Type.QDate)
                layer.addExpressionField('to_date("dateTime")', field)
                field = QgsField("hhmmss", QMetaType.Type.QTime)
                layer.addExpressionField('to_time("dateTime")', field)

            elif layer.name().lower() == FOLLOWERS_TABLE:
                field = QgsField("focalId", QMetaType.Type.QString)
                layer.addExpressionField(
                    "concat(format_date(dateTime,'ddMMyyyy'), '_', computer"
                    ",'_F', _focalId)",
                    field,
                )

            # Add joined fields
            if layer.name().lower() in [SIGHTINGS_TABLE, FOLLOWERS_TABLE]:
                environJoinLayer = QgsVectorLayer(
                    self.session.environmentLayer.source(),
                    self.session.environmentLayer.name(),
                )  # keepped alive until export is done
                field = QgsField("_effortId", QMetaType.Type.QString)
                environJoinLayer.addExpressionField(
                    "to_string(_effortGroup) + '_' + to_string(_effortLeg)",
                    field,
                )
                speciesJoinLayer = QgsVectorLayer(
                    self.session.speciesLayer.source(),
                    self.session.speciesLayer.name(),
                )  # keepped alive until export is done
                layer.addJoin(self.obsEnvLayerJoinInfo(environJoinLayer))
                layer.addJoin(self.obsSpeLayerJoinInfo(speciesJoinLayer))

            elif layer.name() == self.session.environmentLayer.name():
                obsJoinLayerLeft = QgsVectorLayer(
                    self.session.observersLayer.source(),
                    f"{self.session.observersLayer.name()}_left",
                )  # keepped alive until export is done
                left_join = self.environmentLayerJoinObserverInfo(
                    obsJoinLayerLeft, "left"
                )  # keepped alive until export is done
                layer.addJoin(left_join)
                obsJoinLayerRight = QgsVectorLayer(
                    self.session.observersLayer.source(),
                    f"{self.session.observersLayer.name()}_right",
                )  # keepped alive until export is done
                right_join = self.environmentLayerJoinObserverInfo(
                    obsJoinLayerRight, "right"
                )  # keepped alive until export is done
                layer.addJoin(right_join)
                obsJoinLayerCenter = QgsVectorLayer(
                    self.session.observersLayer.source(),
                    f"{self.session.observersLayer.name()}_center",
                )  # keepped alive until export is done
                center_join = self.environmentLayerJoinObserverInfo(
                    obsJoinLayerCenter, "center"
                )  # keepped alive until export is done
                layer.addJoin(center_join)
                plateformJoinLayer = QgsVectorLayer(
                    self.session.plateformLayer.source(),
                    self.session.plateformLayer.name(),
                )
                layer.addJoin(
                    self.environmentLayerJoinPlateformInfo(plateformJoinLayer)
                )
                transectJoinLayer = QgsVectorLayer(
                    self.session.transectLayer.source(),
                    self.session.transectLayer.name(),
                )
                layer.addJoin(
                    self.environmentLayerJoinTransectInfo(transectJoinLayer)
                )
                layer = self.addEndEffortFeature(layer)

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver
            options.attributes = [
                layer.fields().indexOf(field.name())
                for field in layer.fields()
                if field.name()
                not in [
                    "validated",
                    "plateformId",
                    "transectId",
                    "_effortLeg",
                    "_effortGroup",
                    "_focalId",
                    "_effortId",
                    "endDateTime",
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
            if layer.name() == self.session.environmentLayer.name():
                self.removeEndEffort(layer)
            self.progressBar.setValue(int(100 / nb * (i + 1)))
        self.close()

    def obsEnvLayerJoinInfo(self, layer: QgsVectorLayer) -> None:
        environmentJoinInfo = QgsVectorLayerJoinInfo()
        environmentJoinInfo.setJoinLayer(layer)
        environmentJoinInfo.setJoinFieldName("_effortId")
        environmentJoinInfo.setTargetFieldName("_effortId")
        environmentJoinInfo.setPrefix("")
        environmentJoinInfo.setJoinFieldNamesSubset(["session", "routeType"])
        return environmentJoinInfo

    def obsSpeLayerJoinInfo(self, layer: QgsVectorLayer) -> None:
        speciesJoinInfo = QgsVectorLayerJoinInfo()
        speciesJoinInfo.setJoinLayer(layer)
        speciesJoinInfo.setJoinFieldName("species")
        speciesJoinInfo.setTargetFieldName("species")
        speciesJoinInfo.setPrefix("species_")
        speciesJoinInfo.setJoinFieldNamesSubset(
            [
                "name_latin",
                "name_eng",
                "group_eng",
                "family_eng",
                "taxon_eng",
                "name_fr",
                "group_fr",
                "family_fr",
                "taxon_fr",
            ]
        )
        return speciesJoinInfo

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

    def environmentLayerJoinTransectInfo(self, layer: QgsVectorLayer) -> None:
        joinInfo = QgsVectorLayerJoinInfo()
        joinInfo.setJoinLayer(layer)
        joinInfo.setJoinFieldName("fid")
        joinInfo.setTargetFieldName("transectId")
        joinInfo.setPrefix("")
        joinInfo.setJoinFieldNamesSubset(["transect", "strateType", "length"])
        return joinInfo

    def addEndEffortFeature(self, layer: QgsVectorLayer) -> QgsVectorLayer:
        layer.startEditing()
        status_field = QgsField("status", QMetaType.Type.QString, len=5)
        layer.dataProvider().addAttributes([status_field])
        layer.commitChanges()
        layer.startEditing()
        status_idx = layer.fields().indexOf("status")
        changes = {}

        for feat in layer.getFeatures():
            changes[feat.id()] = {
                status_idx: StatusCode.display(StatusCode.BEGIN),
            }
        layer.dataProvider().changeAttributeValues(changes)
        layer.commitChanges()
        layer.startEditing()

        for begin_feature in layer.getFeatures(
            QgsFeatureRequest().addOrderBy("endDateTime", True)
        ):
            feat = QgsVectorLayerUtils.createFeature(layer)
            geom = self.interpolateGeom(begin_feature["endDateTime"])
            feat.setGeometry(geom)
            for attr in feat.fields().names():
                if attr in ["fid", "datetime", "status"]:
                    continue
                feat[attr] = begin_feature[attr]
            feat["datetime"] = begin_feature["endDateTime"]
            feat["status"] = StatusCode.display(StatusCode.END)
            layer.addFeature(feat)
        layer.commitChanges()
        layer.startEditing()
        return layer

    def removeEndEffort(self, layer: QgsVectorLayer) -> None:
        layer.startEditing()
        expr = QgsExpression(
            f"status = '{StatusCode.display(StatusCode.END)}'"
        )
        request = QgsFeatureRequest(expr)
        endFts = [endFt.id() for endFt in layer.getFeatures(request)]
        layer.deleteFeatures(endFts)
        layer.commitChanges()
        layer.startEditing()
        layer.deleteAttributes(
            [
                layer.fields().indexOf("status"),
                layer.fields().indexOf("effortDateTime"),
            ]
        )
        layer.commitChanges()
        layer.startEditing()

    def interpolateGeom(self, dt: QDateTime) -> QgsGeometry:
        request = QgsFeatureRequest().setFilterExpression(
            f"datetime = to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        ftsExact = [ft for ft in self.session.gpsLayer.getFeatures(request)]
        if ftsExact:
            return ftsExact[0].geometry()

        request = QgsFeatureRequest().setFilterExpression(
            f"datetime <= to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        request = request.addOrderBy("dateTime", False)
        bft = None
        for bft in self.session.gpsLayer.getFeatures(request):
            break
        ftBefore = None
        if bft:
            ftBefore = bft

        request = QgsFeatureRequest().setFilterExpression(
            f"datetime >= to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        request = request.addOrderBy("dateTime")
        aft = None
        for aft in self.session.gpsLayer.getFeatures(request):
            break
        ftAfter = None
        if aft:
            ftAfter = aft

        if not ftBefore or not ftAfter:
            return QgsGeometry()

        duration = (
            ftAfter["datetime"].toPyDateTime()
            - ftBefore["datetime"].toPyDateTime()
        ).total_seconds()
        beforePercent = (
            (
                dt.toPyDateTime() - ftBefore["datetime"].toPyDateTime()
            ).total_seconds()
            / duration
            if duration
            else 0
        )
        geom1 = ftBefore.geometry()
        geom2 = ftAfter.geometry()
        if geom1.isNull() or geom2.isNull():
            return QgsGeometry()

        pt1 = geom1.asPoint()
        pt2 = geom2.asPoint()

        return QgsGeometry.fromPointXY(
            QgsGeometryUtils.interpolatePointOnLine(
                pt1.x(), pt1.y(), pt2.x(), pt2.y(), beforePercent
            )
        )
