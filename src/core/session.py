# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .database import SammoDataBase
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QMutex
from qgis.core import (
    QgsVectorLayerUtils,
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
)
from datetime import datetime
from .debug import Debug


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self._directoryPath: str = None
        self._environmentTable: QgsVectorLayer = None
        self._speciesTable: QgsVectorLayer = None
        self._observationTable: QgsVectorLayer = None
        self._followerTable: QgsVectorLayer = None
        self._gpsTable: QgsVectorLayer = None
        self._mutex = QMutex()

    @staticmethod
    def isDataBaseAvailable(directory):
        return SammoDataBase.isDataBaseAvailableInThisDirectory(directory)

    def onCreateSession(self, directory):
        self._directoryPath = directory
        if not self.isDataBaseAvailable(directory):
            # No geopackage DB in this directory
            self.createEmptyDataBase(directory)

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

    def onStopEffort(self):
        table = self._environmentTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(
            self._environmentTable
        )
        field_idx = table.fields().indexOf(
            SammoDataBase.ENVIRONMENT_COMMENT_FIELD_NAME
        )
        timeOfStopEffort = (
            "End of the Effort at : " + self.nowToString()
        )
        if not table.changeAttributeValue(
            idLastAddedFeature, field_idx, timeOfStopEffort
        ):
            Debug.error("Echec de la modification du champs commentaire")

        table.commitChanges()

    def createEmptyDataBase(self, directory: str):
        self.db.createEmptyDataBase(directory)

        speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        SammoDataBase.initializeSpeciesTable(speciesTable)

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self._directoryPath, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(self._environmentTable)

    def addNewFeatureToEnvironmentTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._environmentTable)

    def getReadyToAddNewFeatureToObservationTable(self):
        return self._getReadyToAddNewFeature(self._observationTable)

    def addNewFeatureToObservationTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._observationTable)

    def addNewFeatureToGpsTable(self, longitude: float, latitude: float):
        self._gpsTable.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(self._gpsTable))
        feature.setAttribute(SammoDataBase.GPS_TIME_FIELD_NAME, self.nowToString())
        feature.setAttribute(SammoDataBase.GPS_LONGITUDE_FIELD_NAME, longitude)
        feature.setAttribute(SammoDataBase.GPS_LATITUDE_FIELD_NAME, latitude)

        self._addNewFeature(feature, self._gpsTable)

    @staticmethod
    def _getReadyToAddNewFeature(table: QgsVectorLayer):
        feat = QgsFeature(QgsVectorLayerUtils.createFeature(table))
        table.startEditing()

        return [feat, table]

    @staticmethod
    def _addNewFeature(feature: QgsFeature, table: QgsVectorLayer):
        try:
            if not table.addFeature(feature):
                Debug.error("addFeature : échec ")

            if not table.commitChanges():
                Debug.error("_addNewFeatureThreadSafe : échec ")
        except:
            Debug.error("_addNewFeatureThreadSafe : exception ")

    @staticmethod
    def nowToString() -> str:
        dateTimeObj = datetime.now()
        time = (
            "{:02d}".format(dateTimeObj.day)
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
        return time
