# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis.PyQt.QtWidgets import (
    QLabel,
    QDialog,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDateTimeEdit,
)
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsGeometry,
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
        self.setWindowTitle(f"Duplicate {layer.name()} entity")
        self.gpsLayer: QgsVectorLayer = gpsLayer
        self.toDuplicate: QgsFeature = self.layer.getFeature(toDuplicate)
        self.validateButton = QPushButton("Duplicate with changes")
        self.validateButton.clicked.connect(self.validate)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)

        self.VLayout = QVBoxLayout(self)
        # datetime
        self.HLayout = QHBoxLayout()
        self.datetimeLabel = QLabel("Datetime :")
        self.datetimeEdit = QDateTimeEdit(self.toDuplicate["datetime"])
        self.datetimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.HLayout.addWidget(self.datetimeLabel)
        self.HLayout.addWidget(self.datetimeEdit)
        self.VLayout.addLayout(self.HLayout)
        self.geometryLabel = QLabel("")
        self.datetimeEdit.dateTimeChanged.connect(self.updateGeometry)
        self.VLayout.addWidget(self.geometryLabel)
        if self.layer.name() == "Environment":
            self.HStatusLayout = QHBoxLayout()
            self.statusLabel = QLabel("Status :")
            self.statusComboBox = QComboBox()
            self.statusComboBox.addItems(
                [
                    [k for k in element.keys()][0]
                    for element in self.layer.editorWidgetSetup(
                        self.layer.fields().indexOf("status")
                    ).config()["map"]
                ]
            )
            self.statusComboBox.setCurrentIndex(
                self.statusComboBox.findText(self.toDuplicate["status"])
            )
            self.HStatusLayout.addWidget(self.statusLabel)
            self.HStatusLayout.addWidget(self.statusComboBox)
            self.VLayout.addLayout(self.HStatusLayout)

            self.HEffortLayout = QHBoxLayout()
            self.effortLabel = QLabel("effortGroup :")
            self.effortComboBox = QComboBox()
            self.effortComboBox.addItems(
                [
                    str(element)
                    for element in self.layer.uniqueValues(
                        self.layer.fields().indexOf("effortGroup")
                    )
                ]
            )
            self.effortComboBox.setCurrentIndex(
                self.effortComboBox.findText(
                    str(self.toDuplicate["effortGroup"])
                )
            )
            self.HEffortLayout.addWidget(self.effortLabel)
            self.HEffortLayout.addWidget(self.effortComboBox)
            self.VLayout.addLayout(self.HEffortLayout)

            self.updateGeometry()

        self.HBottomLayout = QHBoxLayout()
        self.HBottomLayout.addWidget(self.cancelButton)
        self.HBottomLayout.addWidget(self.validateButton)
        self.VLayout.addLayout(self.HBottomLayout)

    def validate(self):
        feat = QgsVectorLayerUtils.createFeature(self.layer)
        feat.setGeometry(self.interpolated)

        for name in self.toDuplicate.fields().names():
            if name == "fid":
                continue
            feat[name] = self.toDuplicate[name]

        feat["datetime"] = self.datetimeEdit.dateTime()
        if self.layer.name() == "Environment":
            feat["status"] = self.statusComboBox.currentText()
            feat["effortGroup"] = int(self.effortComboBox.currentText())

        self.layer.startEditing()
        self.layer.addFeature(feat)
        self.layer.commitChanges()
        self.layer.startEditing()
        self.close()

    def updateGeometry(self):
        dt = self.datetimeEdit.dateTime()
        request = QgsFeatureRequest().setFilterExpression(
            f"datetime = to_datetime('{dt.toPyDateTime().isoformat()}')"
        )
        ftsExact = [ft for ft in self.gpsLayer.getFeatures(request)]
        if ftsExact:
            self.interpolated = ftsExact[0].geometry()
            self.geometryLabel.setText(
                f"Interpolated position : {self.interpolated.asWkt()}"
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
            f"Interpolated position : {self.interpolated.asWkt()}"
        )


toDuplicate = int("[%fid%]")
layerId = "[%@layer_id%]"
gpsLayers = QgsProject.instance().mapLayersByName("GPS")
if gpsLayers:
    dlg = DuplicateDialog(toDuplicate, layerId, gpsLayers[0])
    dlg.show()
