# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis import utils
from qgis.PyQt.QtWidgets import (
    QLabel,
    QDialog,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDateTimeEdit,
)
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsExpression,
    QgsVectorLayer,
    QgsGeometryUtils,
    QgsFeatureRequest,
    QgsVectorLayerUtils,
)


class DuplicateDialog(QDialog):
    def __init__(
        self, toDuplicate: int, layerId: str, gpsLayer: QgsVectorLayer
    ):
        super().__init__()
        self.layer: QgsVectorLayer = QgsProject.instance().mapLayer(layerId)
        self.setWindowTitle(f"Duplicate {self.layer.name().lower()} entity")
        self.gpsLayer: QgsVectorLayer = gpsLayer
        self.toDuplicate: QgsFeature = self.layer.getFeature(toDuplicate)
        self.validateButton = QPushButton("Duplicate with changes")
        self.validateButton.clicked.connect(self.validate)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)

        self.VLayout = QVBoxLayout(self)
        self.checkBox = QCheckBox("Duplicate ?")
        self.checkBox.setChecked(True)
        self.VLayout.addWidget(self.checkBox)
        # datetime
        self.HLayout = QHBoxLayout()
        self.datetimeLabel = QLabel("Datetime :")
        self.datetimeEdit = QDateTimeEdit(self.toDuplicate["dateTime"])
        self.datetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.HLayout.addWidget(self.datetimeLabel)
        self.HLayout.addWidget(self.datetimeEdit)
        self.endDatetimeLabel = QLabel("End Datetime :")
        self.endDatetimeEdit = QDateTimeEdit(self.toDuplicate["endDateTime"])
        self.endDatetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.HendLayout = QHBoxLayout()
        self.HendLayout.addWidget(self.endDatetimeLabel)
        self.HendLayout.addWidget(self.endDatetimeEdit)
        self.VLayout.addLayout(self.HLayout)
        self.VLayout.addLayout(self.HendLayout)
        self.geometryLabel = QLabel("")
        self.datetimeEdit.dateTimeChanged.connect(self.updateGeometry)
        self.VLayout.addWidget(self.geometryLabel)
        self.updateGeometry()

        self.HBottomLayout = QHBoxLayout()
        self.HBottomLayout.addWidget(self.cancelButton)
        self.HBottomLayout.addWidget(self.validateButton)
        self.VLayout.addLayout(self.HBottomLayout)

    def validate(self):
        if self.checkBox.isChecked():
            feat = QgsVectorLayerUtils.createFeature(self.layer)
            feat.setGeometry(self.interpolated)

            for name in self.toDuplicate.fields().names():
                if name == "fid":
                    continue
                feat[name] = self.toDuplicate[name]

            dt = self.datetimeEdit.dateTime()
            endDt = self.endDatetimeEdit.dateTime()
            feat["datetime"] = dt
            feat["endDateTime"] = endDt

            self.layer.startEditing()
            self.layer.addFeature(feat)

            request = QgsFeatureRequest(
                QgsExpression(
                    "dateTime < to_datetime("
                    f"'{dt.toPyDateTime().isoformat()}')"
                )
            )
            prevFeat = None
            for prevFeat in self.layer.getFeatures(request):
                break
            if prevFeat:
                if prevFeat["endDateTime"] > feat["dateTime"]:
                    prevFeat["endDateTime"] = self.datetimeEdit.dateTime()
                    self.layer.updateFeature(prevFeat)

        else:
            self.layer.startEditing()
            self.layer.changeGeometry(self.toDuplicate.id(), self.interpolated)
            self.layer.changeAttributeValue(
                self.toDuplicate.id(),
                self.layer.fields().indexOf("dateTime"),
                self.datetimeEdit.dateTime(),
            )
            self.layer.changeAttributeValue(
                self.toDuplicate.id(),
                self.layer.fields().indexOf("endDateTime"),
                self.endDatetimeEdit.dateTime(),
            )
        self.layer.commitChanges()
        self.layer.startEditing()
        self.close()
        for pluginInstance in utils.plugins.values():
            if pluginInstance.__class__.__name__ == "Sammo":
                pluginInstance.filterTable()

    def updateGeometry(self):
        dt = self.datetimeEdit.dateTime()
        request = QgsFeatureRequest().setFilterExpression(
            f"datetime = to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        ftsExact = [ft for ft in self.gpsLayer.getFeatures(request)]
        if ftsExact:
            self.interpolated = ftsExact[0].geometry()
            self.geometryLabel.setText(
                f"Interpolated position : {self.interpolated.asWkt(3)}"
            )
            return

        request = QgsFeatureRequest().setFilterExpression(
            f"datetime <= to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        request = request.addOrderBy("dateTime", False)
        ftsBefore = [ft for ft in self.gpsLayer.getFeatures(request)]
        ftBefore = None
        if ftsBefore:
            ftBefore = ftsBefore[0]

        request = QgsFeatureRequest().setFilterExpression(
            f"datetime >= to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        request = request.addOrderBy("dateTime")
        ftsAfter = [ft for ft in self.gpsLayer.getFeatures(request)]
        ftAfter = None
        if ftsAfter:
            ftAfter = ftsAfter[0]

        if not ftBefore or not ftAfter:
            self.geometryLabel.setText(
                "Interpolated position : datetime out of bounds"
            )
            self.interpolated = QgsGeometry()
            return
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
            self.geometryLabel.setText(
                "Interpolated position : closest record geometries are "
                "not valid"
            )
            self.interpolated = QgsGeometry()
            return
        pt1 = geom1.asPoint()
        pt2 = geom2.asPoint()

        self.interpolated = QgsGeometry.fromPointXY(
            QgsGeometryUtils.interpolatePointOnLine(
                pt1.x(), pt1.y(), pt2.x(), pt2.y(), beforePercent
            )
        )
        self.geometryLabel.setText(
            f"Interpolated position : {self.interpolated.asWkt(3)}"
        )


toDuplicate = int("[%fid%]")
layerId = "[%@layer_id%]"
gpsLayers = QgsProject.instance().mapLayersByName("GPS")
if gpsLayers:
    dlg = DuplicateDialog(toDuplicate, layerId, gpsLayers[0])
    dlg.show()
