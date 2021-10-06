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
from .database import SammoDataBase, GPS_TABLE, DB_NAME, ENVIRONMENT_TABLE


class SammoSession:
    def __init__(self, mapCanvas: QgsMapCanvas):
        self.mapCanvas: QgsMapCanvas = mapCanvas
        self.db = SammoDataBase()
        self._gpsLocationsDuringEffort = []
        self._lastEnvironmentFeature: QgsFeature = None

    @property
    def environmentLayer(self) -> QgsVectorLayer:
        return self._layer(ENVIRONMENT_TABLE)

    @property
    def gpsLayer(self) -> QgsVectorLayer:
        return self._layer(GPS_TABLE)

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
            table = self.observationLayer
        else:
            table = self.environmentLayer

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
        layer = self.environmentLayer
        feat = self._getReadyToAddNewFeature(layer)

        if self._lastEnvironmentFeature:
            feat = self.copyEnvironmentFeature(self._lastEnvironmentFeature)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feat["status"] = status
        return feat, layer

    def addEnvironment(self, feature: QgsFeature) -> None:
        vlayer = self.environmentLayer
        vlayer.startEditing()
        self._addFeature(feature, vlayer)
        # self._lastEnvironmentFeature = self.copyEnvironmentFeature(feature)
        # self._gpsLocationsDuringEffort = []

    def copyEnvironmentFeature(self, feat: QgsFeature) -> QgsFeature:
        copyFeature = QgsVectorLayerUtils.createFeature(self._environmentTable)
        for field in feat.fields():
            copyFeature[field.name()] = feat[field.name()]
        return copyFeature

    def addFollower(self, feature: QgsFeature):
        self._addFeature(feature, self._followerTable)

    def getReadyToAddNewFeatureToObservationTable(
        self,
    ) -> (QgsFeature, QgsVectorLayer):
        (
            feat,
            table,
        ) = self._getReadyToAddNewFeature(self._observationTable)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return feat, table

    def addObservation(self, feature: QgsFeature):
        self._addFeature(feature, self._observationTable)

    def addGps(
        self, longitude: float, latitude: float, formattedDateTime: str
    ):
        vlayer = self.gpsLayer
        vlayer.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(vlayer))
        point = QgsPointXY(longitude, latitude)
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        feature.setAttribute("dateTime", formattedDateTime)

        self._addFeature(feature, vlayer)
        self._gpsLocationsDuringEffort.append(QgsPoint(longitude, latitude))

    def _layer(self, name: str) -> QgsVectorLayer:
        return QgsVectorLayer(self.db.tableUri(name))

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
        layer: QgsVectorLayer,
    ) -> (QgsFeature, QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(layer)
        layer.startEditing()
        return feat

    @staticmethod
    def _addFeature(feature: QgsFeature, vlayer: QgsVectorLayer) -> None:
        if not vlayer.addFeature(feature):
            Logger.error("addFeature : échec ")
        if not vlayer.commitChanges():
            Logger.error("_addFeatureThreadSafe : échec ")

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
