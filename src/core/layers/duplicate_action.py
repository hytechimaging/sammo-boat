# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis import utils
from qgis.PyQt.QtCore import Qt, QDateTime
from qgis.PyQt.QtWidgets import (
    QLabel,
    QDialog,
    QCheckBox,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDateTimeEdit,
)
from qgis.core import (
    NULL,
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
        self.checkBox.stateChanged.connect(self.validateLabelChange)
        # datetime
        self.HLayout = QHBoxLayout()
        self.datetimeLabel = QLabel("Datetime :")
        self.datetimeEdit = QDateTimeEdit()
        self.datetimeEdit.setTimeSpec(Qt.UTC)
        self.datetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.datetimeEdit.setDateTime(self.toDuplicate["dateTime"])
        self.HLayout.addWidget(self.datetimeLabel)
        self.HLayout.addWidget(self.datetimeEdit)
        self.VLayout.addLayout(self.HLayout)
        if self.layer.name().lower() == "environment":
            self.endDatetimeLabel = QLabel("End Datetime :")
            self.endDatetimeEdit = QDateTimeEdit()
            self.endDatetimeEdit.setTimeSpec(Qt.UTC)
            self.endDatetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
            if self.toDuplicate["endDateTime"] != NULL:
                self.endDatetimeEdit.setDateTime(
                    self.toDuplicate["endDateTime"]
                )
            self.endDatetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
            self.HendLayout = QHBoxLayout()
            self.HendLayout.addWidget(self.endDatetimeLabel)
            self.HendLayout.addWidget(self.endDatetimeEdit)
            self.VLayout.addLayout(self.HendLayout)

            obsLyr = QgsProject.instance().mapLayersByName("Observers")[0]
            obsIdx = obsLyr.fields().indexOf("observer")
            obsValues = obsLyr.uniqueValues(obsIdx)

            self.observerLayout = QHBoxLayout()
            self.leftComboBox = QComboBox()
            self.centerComboBox = QComboBox()
            self.rightComboBox = QComboBox()
            for side, comboBox in zip(
                ["(Left)", "(Center)", "(Right)"],
                [self.leftComboBox, self.centerComboBox, self.rightComboBox],
            ):
                comboBox.addItem(side, NULL)
            for name in obsValues:
                self.leftComboBox.addItem(name, name)
                self.centerComboBox.addItem(name, name)
                self.rightComboBox.addItem(name, name)
            for comboBox in [
                self.leftComboBox,
                self.centerComboBox,
                self.rightComboBox,
            ]:
                if comboBox.currentIndex() == -1:
                    comboBox.setCurrentIndex(0)

            self.observerLayout.addWidget(self.leftComboBox)
            self.observerLayout.addWidget(self.centerComboBox)
            self.observerLayout.addWidget(self.rightComboBox)

            self.leftComboBox.setCurrentIndex(
                max(self.leftComboBox.findData(self.toDuplicate["left"]), 0)
            )
            self.centerComboBox.setCurrentIndex(
                max(
                    self.centerComboBox.findData(self.toDuplicate["center"]), 0
                )
            )
            self.rightComboBox.setCurrentIndex(
                max(self.rightComboBox.findData(self.toDuplicate["right"]), 0)
            )
            self.VLayout.addLayout(self.observerLayout)

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
            dt = QDateTime(dt.date(), dt.time(), Qt.UTC)
            feat["datetime"] = dt
            if self.layer.name().lower() == "environment":
                endDt = QDateTime(endDt.date(), endDt.time(), Qt.UTC)
                feat["endDateTime"] = endDt
                feat["left"] = self.leftComboBox.currentData()
                feat["center"] = self.centerComboBox.currentData()
                feat["right"] = self.rightComboBox.currentData()
            self.layer.startEditing()
            self.layer.addFeature(feat)

            # Update previous feature if needed
            if self.layer.name().lower() == "environment":
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
            dt = self.datetimeEdit.dateTime()
            dt = QDateTime(dt.date(), dt.time(), Qt.UTC)
            self.layer.changeAttributeValue(
                self.toDuplicate.id(),
                self.layer.fields().indexOf("dateTime"),
                dt,
            )
            if self.layer.name().lower() == "environment":
                endDt = self.endDatetimeEdit.dateTime()
                endDt = QDateTime(endDt.date(), endDt.time(), Qt.UTC)
                self.layer.changeAttributeValue(
                    self.toDuplicate.id(),
                    self.layer.fields().indexOf("endDateTime"),
                    endDt,
                )
                self.layer.changeAttributeValue(
                    self.toDuplicate.id(),
                    self.layer.fields().indexOf("left"),
                    self.leftComboBox.currentData(),
                )
                self.layer.changeAttributeValue(
                    self.toDuplicate.id(),
                    self.layer.fields().indexOf("center"),
                    self.centerComboBox.currentData(),
                )
                self.layer.changeAttributeValue(
                    self.toDuplicate.id(),
                    self.layer.fields().indexOf("right"),
                    self.rightComboBox.currentData(),
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

    def validateLabelChange(self, state: int) -> None:
        if state:
            self.validateButton.setText("Duplicate with changes")
            return
        self.validateButton.setText("Apply changes")


toDuplicate = int("[%fid%]")
layerId = "[%@layer_id%]"
gpsLayers = QgsProject.instance().mapLayersByName("GPS")
if gpsLayers:
    dlg = DuplicateDialog(toDuplicate, layerId, gpsLayers[0])
    dlg.show()
