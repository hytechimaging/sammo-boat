# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
import platform
from datetime import datetime

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (
    QgsPoint,
    QgsFeature,
    QgsPointXY,
    QgsProject,
    QgsGeometry,
    QgsApplication,
    QgsVectorLayer,
    QgsVectorLayerUtils,
    QgsCoordinateReferenceSystem,
)

from .logger import Logger
from .database import SammoDataBase


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.directory: str = ""
        self._environmentTable: QgsVectorLayer = None
        self._speciesTable: QgsVectorLayer = None
        self._observationTable: QgsVectorLayer = None
        self._followerTable: QgsVectorLayer = None
        self._gpsTable: QgsVectorLayer = None
        self._gpsLocationsDuringEffort = []
        self._lastEnvironmentFeature: QgsFeature = None

    @staticmethod
    def exist(directory: str) -> bool:
        return SammoDataBase.exist(directory)

    def onLoadProject(self, directory):
        self.directory = directory
        self._loadTables()
        self._configureAutoRefreshLayers()

    def init(self, directory):
        self.directory = directory
        uri = (
            "geopackage:"
            + SammoDataBase.pathToDataBase(directory)
            + "?projectName=project"
        )

        if not self.exist(directory):
            # No geopackage DB in this directory
            self.create(directory)

            project = QgsProject()
            gpsTable = self.loadTable(SammoDataBase.GPS_TABLE_NAME)
            project.addMapLayer(gpsTable)
            layerWorldMap = QgsVectorLayer(self._worldMapPath())
            layerWorldMap.setName("world_map")
            project.addMapLayer(layerWorldMap)
            project.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(4326))
            project.write(uri)  # Save the QGIS projet into the database

        QgsProject.instance().read(uri)
        self._loadTables()
        self._configureAutoRefreshLayers()

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

    def _loadTables(self):
        self._environmentTable = self.loadTable(
            SammoDataBase.ENVIRONMENT_TABLE_NAME
        )
        self._speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        self._observationTable = self.loadTable(
            SammoDataBase.OBSERVATION_TABLE_NAME
        )
        self._followerTable = self.loadTable(SammoDataBase.FOLLOWER_TABLE_NAME)
        self._gpsTable = self.loadTable(SammoDataBase.GPS_TABLE_NAME)

    @staticmethod
    def _configureAutoRefreshLayers():
        layer = QgsProject.instance().mapLayersByName("gps")[0]
        layer.setAutoRefreshInterval(1000)
        layer.setAutoRefreshEnabled(True)

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

    def create(self, directory: str) -> None:
        self.db.create(directory)

        speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        SammoDataBase.initializeSpeciesTable(speciesTable)

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
