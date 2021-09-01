# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt.QtWidgets import QMessageBox
from .database import SammoDataBase
from .logger import Logger
from datetime import datetime
from qgis.core import (
    QgsVectorLayerUtils,
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsPoint,
)


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.directoryPath: str = None
        self._environmentTable: QgsVectorLayer = None
        self._speciesTable: QgsVectorLayer = None
        self._observationTable: QgsVectorLayer = None
        self._followerTable: QgsVectorLayer = None
        self._gpsTable: QgsVectorLayer = None
        self._gpsLocationsDuringEffort = []

    @staticmethod
    def isDataBaseAvailable(directory):
        return SammoDataBase.isDataBaseAvailableInThisDirectory(directory)

    def onCreateSession(self, directory):
        self.directoryPath = directory
        isNewDataBase = False
        if not self.isDataBaseAvailable(directory):
            # No geopackage DB in this directory
            self.createEmptyDataBase(directory)
            isNewDataBase = True

        self._environmentTable = self.loadTable(
            SammoDataBase.ENVIRONMENT_TABLE_NAME
        )
        self._speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        self._observationTable = self.loadTable(
            SammoDataBase.OBSERVATION_TABLE_NAME
        )
        self._followerTable = self.loadTable(SammoDataBase.FOLLOWER_TABLE_NAME)
        self._gpsTable = self.loadTable(SammoDataBase.GPS_TABLE_NAME)

        QgsProject.instance().addMapLayer(self._gpsTable)
        if isNewDataBase:
            # Save the QGIS projet into the database
            uri = "geopackage:" + SammoDataBase.pathToDataBase(directory) + "?projectName=sammo_boat_project"
            QgsProject.instance().write(uri)

    def onStopSoundRecordingForObservation(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        table = self._observationTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        field_idx = table.fields().indexOf("fichier_son")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundFile)
        field_idx = table.fields().indexOf("sound_start")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundStart)
        field_idx = table.fields().indexOf("sound_end")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundEnd)
        table.commitChanges()

    def onStopEffort(self):
        table = self._environmentTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        field_idx = table.fields().indexOf(
            SammoDataBase.ENVIRONMENT_COMMENT_FIELD_NAME
        )
        dateTimeObj = datetime.now()
        timeOfStopEffort = (
            "End of the Effort at : "
            + "{:02d}".format(dateTimeObj.day)
            + "/"
            + "{:02d}".format(dateTimeObj.month)
            + "/"
            + str(dateTimeObj.year)
            + " "
            + "{:02d}".format(dateTimeObj.hour)
            + ":"
            + "{:02d}".format(dateTimeObj.minute)
            + ":"
            + "{:02d}".format(dateTimeObj.second)
        )
        table.changeAttributeValue(
            idLastAddedFeature, field_idx, timeOfStopEffort
        )
        table.changeGeometry(
            idLastAddedFeature,
            QgsGeometry.fromPolyline(self._gpsLocationsDuringEffort),
        )
        table.commitChanges()

    def createEmptyDataBase(self, directory: str):
        self.db.createEmptyDataBase(directory)

        speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        SammoDataBase.initializeSpeciesTable(speciesTable)

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self.directoryPath, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def getReadyToAddNewFeatureToFollowerTable(self):
        return self._getReadyToAddNewFeature(self._followerTable)

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(self._environmentTable)

    def onStartEffort(self, feature: QgsFeature):
        self._addNewFeature(feature, self._environmentTable)
        self._gpsLocationsDuringEffort = []

    def addNewFeatureToFollowerTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._followerTable)

    def getReadyToAddNewFeatureToObservationTable(
        self,
    ) -> (QgsFeature, QgsVectorLayer):
        return self._getReadyToAddNewFeature(self._observationTable)

    def addNewFeatureToObservationTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._observationTable)

    def addNewFeatureToGpsTable(
        self, longitude: float, latitude: float, leg_heure: str, code_leg: int
    ):
        self._gpsTable.startEditing()
        feature = QgsFeature(QgsVectorLayerUtils.createFeature(self._gpsTable))
        layerPoint = QgsPointXY(longitude, latitude)
        feature.setGeometry(QgsGeometry.fromPointXY(layerPoint))
        feature.setAttribute("leg_heure", leg_heure)
        feature.setAttribute("code_leg", code_leg)

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
