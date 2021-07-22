# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .database import SammoDataBase
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayerUtils, QgsVectorLayer
from datetime import datetime


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.isDbOpened = False
        self._directoryPath: str = None
        self._environmentTable: QgsVectorLayer = None

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
        if not self._environmentTable.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the environment table ",
            )

    def onStopEffort(self):
        table = self._environmentTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(
            self._environmentTable
        )
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
        if not table.changeAttributeValue(
            idLastAddedFeature, field_idx, timeOfStopEffort
        ):
            print("Echec de la modification du champs commentaire")

        table.commitChanges()

    def createEmptyDataBase(self, directory):
        self.db.createEmptyDataBase(directory)

    def loadTable(self, tableName):
        return self.db.loadTable(self._directoryPath, tableName)

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(self._environmentTable)

    def addNewFeatureToEnvironmentTable(self, feat):
        self._environmentTable.addFeature(feat)
        self._environmentTable.commitChanges()

    @staticmethod
    def _getReadyToAddNewFeature(table: QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()
        return feat, table
      