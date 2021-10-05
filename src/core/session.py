# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
import platform
from datetime import datetime

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.gui import QgsMapCanvas
from qgis.core import (
    QgsPoint,
    QgsFeature,
    QgsPointXY,
    QgsProject,
    QgsGeometry,
    QgsMapLayer,
    QgsApplication,
    QgsVectorLayer,
    QgsVectorLayerUtils,
    QgsReferencedRectangle,
    QgsCoordinateReferenceSystem,
)

from .logger import Logger
from .database import SammoDataBase, GPS_TABLE, DB_NAME


class SammoSession:
    def __init__(self, mapCanvas: QgsMapCanvas):
        self.mapCanvas: QgsMapCanvas = mapCanvas
        self.db = SammoDataBase()
        self._gpsLocationsDuringEffort = []
        self._lastEnvironmentFeature: QgsFeature = None

    def init(self, directory: str) -> None:
        extent = self.mapCanvas.projectExtent()
        new = self.db.init(directory)

        # create database if necessary
        if new:
            project = QgsProject()
            crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)

            worldLayer = QgsVectorLayer(SammoSession._worldMapPath(), "World")
            symbol = worldLayer.renderer().symbol()
            symbol.setColor(QColor(178, 223, 138))
            project.addMapLayer(worldLayer)

            extent = QgsReferencedRectangle(worldLayer.extent(), crs)
            project.viewSettings().setDefaultViewExtent(extent)

            gpsLayer = QgsVectorLayer(self.db.tableUri(GPS_TABLE), "GPS")
            symbol = gpsLayer.renderer().symbol()
            symbol.setColor(QColor(219, 30, 42))
            symbol.setSize(2)
            gpsLayer.setAutoRefreshInterval(1000)
            gpsLayer.setAutoRefreshEnabled(True)
            project.addMapLayer(gpsLayer)

            project.setCrs(crs)
            project.setBackgroundColor(QColor(166, 206, 227))
            self.db.writeProject(project)

        # read project
        QgsProject.instance().read(self.db.projectUri)

    def onStopSoundRecordingForEvent(
        self,
        isObservation: bool,
        soundFile: str,
        soundStart: str,
        soundEnd: str,
    ):
        if isObservation:
            table = self._observationTable
        else:
            table = self._environmentTable

        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        field_idx = table.fields().indexOf("fichier_son")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundFile)
        field_idx = table.fields().indexOf("sound_start")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundStart)
        field_idx = table.fields().indexOf("sound_end")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundEnd)
        table.commitChanges()

    def onStopTransect(self):
        if 0 == len(self._gpsLocationsDuringEffort):
            return
        table = self._environmentTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        table.changeGeometry(
            idLastAddedFeature,
            QgsGeometry.fromPolyline(self._gpsLocationsDuringEffort),
        )
        table.commitChanges()

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self.directory, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def getReadyToAddNewFeatureToFollowerTable(self):
        return self._getReadyToAddNewFeature(self._followerTable)

    def getReadyToAddNewFeatureToEnvironmentTable(
        self, status: str
    ) -> (QgsFeature, QgsVectorLayer):
        (
            feat,
            table,
        ) = self._getReadyToAddNewFeature(self._environmentTable)
        if self._lastEnvironmentFeature:
            feat = self.copyEnvironmentFeature(self._lastEnvironmentFeature)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feat["status"] = status
        return feat, table

    def addNewFeatureToEnvironmentTable(self, feature: QgsFeature):
        self._environmentTable.startEditing()
        self._addNewFeature(feature, self._environmentTable)
        self._lastEnvironmentFeature = self.copyEnvironmentFeature(feature)
        self._gpsLocationsDuringEffort = []

    def copyEnvironmentFeature(self, feat: QgsFeature) -> QgsFeature:
        copyFeature = QgsVectorLayerUtils.createFeature(self._environmentTable)
        for field in feat.fields():
            copyFeature[field.name()] = feat[field.name()]
        return copyFeature

    def addNewFeatureToFollowerTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._followerTable)

    def getReadyToAddNewFeatureToObservationTable(
        self,
    ) -> (QgsFeature, QgsVectorLayer):
        (
            feat,
            table,
        ) = self._getReadyToAddNewFeature(self._observationTable)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return feat, table

    def addNewFeatureToObservationTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._observationTable)

    def addNewFeatureToGpsTable(
        self, longitude: float, latitude: float, formattedDateTime: str
    ):
        if not self._gpsTable:
            return
        self._gpsTable.startEditing()
        feature = QgsFeature(QgsVectorLayerUtils.createFeature(self._gpsTable))
        layerPoint = QgsPointXY(longitude, latitude)
        feature.setGeometry(QgsGeometry.fromPointXY(layerPoint))
        feature.setAttribute("dateTime", formattedDateTime)

        self._addNewFeature(feature, self._gpsTable)
        self._gpsLocationsDuringEffort.append(QgsPoint(longitude, latitude))

    @staticmethod
    def sessionDirectory(project: QgsProject) -> str:
        for layer in project.mapLayers().values():
            if layer.type() != QgsMapLayer.VectorLayer:
                continue

            uri = layer.dataProvider().dataSourceUri()
            if DB_NAME in uri:
                return uri.split("|")[0].replace(DB_NAME, "")

        return ""

    @staticmethod
    def _getReadyToAddNewFeature(
        table: QgsVectorLayer,
    ) -> (QgsFeature, QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()
        return feat, table

    @staticmethod
    def _addNewFeature(feature: QgsFeature, table: QgsVectorLayer):
        if not table.addFeature(feature):
            Logger.error("addFeature : échec ")
        if not table.commitChanges():
            Logger.error("_addNewFeatureThreadSafe : échec ")

    @staticmethod
    def _worldMapPath() -> str:
        path = QgsApplication.instance().pkgDataPath()
        if platform.system() == "Windows":
            path = os.path.join(
                path, "resources", "data", "world_map.gpkg|layername=countries"
            )
        else:
            path = os.path.join(
                path,
                "resources",
                "data",
                "world_map.gpkg|layername=countries",
            )
        return path
