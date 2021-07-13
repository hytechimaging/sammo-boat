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
            "End of the Effort at : "
            + self.nowToStringThreadSafe()
        )
        if not table.changeAttributeValue(
            idLastAddedFeature, field_idx, timeOfStopEffort
        ):
            print("Echec de la modification du champs commentaire")

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
        self._addNewFeatureThreadSafe(feature, self._environmentTable)

    def getReadyToAddNewFeatureToObservationTable(self):
        return self._getReadyToAddNewFeature(self._observationTable)

    def addNewFeatureToObservationTable(self, feature: QgsFeature):
        self._addNewFeatureThreadSafe(feature, self._observationTable)

    def addNewFeatureToGpsTable(self, longitude: float, latitude: float):
        # this methode is usually called from a thread different from the main one
        self._gpsTable.startEditing();

        time = self.nowToStringThreadSafe()

        feature = self._createFeatureThreadSafe(self._gpsTable)

        if (True == self._setAttributeThreadSafe(feature, SammoDataBase.GPS_TIME_FIELD_NAME, time)):
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_TIME_FIELD_NAME : ok ")
        else:
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_TIME_FIELD_NAME : échec ")

        if (True == self._setAttributeThreadSafe(feature, SammoDataBase.GPS_LONGITUDE_FIELD_NAME, longitude)):
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_LONGITUDE_FIELD_NAME : ok ")
        else:
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_LONGITUDE_FIELD_NAME : échec ")

        if (True == self._setAttributeThreadSafe(feature, SammoDataBase.GPS_LATITUDE_FIELD_NAME, latitude)):
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_LATITUDE_FIELD_NAME : ok ")
        else:
            print("_setAttributeThreadSafe(feature, SammoDataBase.GPS_LATITUDE_FIELD_NAME : échec ")

        self._addNewFeatureThreadSafe(feature, self._gpsTable)

    def _getReadyToAddNewFeature(self, table: QgsVectorLayer):
        feat = self._createFeatureThreadSafe(table)
        table.startEditing()

        return [feat, table]

    def _setAttributeThreadSafe(self, feature: QgsFeature, fieldName: str, value) -> bool :
        self._mutex.lock()
        result = feature.setAttribute(fieldName, value)
        self._mutex.unlock()
        return result

    def _addNewFeatureThreadSafe(self, feature: QgsFeature, table: QgsVectorLayer):
        self._mutex.lock()

        if (True == table.addFeature(feature)):
            print("addFeature : ok ")
        else:
            print("addFeature : échec ")

        if (True == table.commitChanges()):
            print("_addNewFeatureThreadSafe : ok ")
        else:
            print("_addNewFeatureThreadSafe : échec ")

        self._mutex.unlock()

    def _createFeatureThreadSafe(self, table: QgsVectorLayer) -> QgsFeature:
        self._mutex.lock()
        feature = QgsFeature(QgsVectorLayerUtils.createFeature(table))
        self._mutex.unlock()
        return feature

    def nowToStringThreadSafe(self) -> str:
            self._mutex.lock()
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
            self._mutex.unlock()
            return time
