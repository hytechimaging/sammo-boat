# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .database import SammoDataBase
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayerUtils, QgsVectorLayer


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.isDbOpened = False
        self._directoryPath = None
        self._environmentTable = None

    @staticmethod
    def isDataBaseAvailable(directory):
        return SammoDataBase.isDataBaseAvailableInThisDirectory(directory)

    def onCreateSession(self, directory):
        self._directoryPath = directory
        if not self.isDataBaseAvailable(directory):
            # No geopackage DB in this directory
            self.createEmptyDataBase(directory)

        self._environmentTable = self.loadTable(SammoDataBase.ENVIRONMENT_TABLE_NAME)
        if not self._environmentTable.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the environment table "
            )

    def createEmptyDataBase(self, directory):
        self.db.createEmptyDataBase(directory)

    def loadTable(self, tableName):
        return self.db.loadTable(self._directoryPath, tableName)

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(self._environmentTable)

    def addNewFeatureToEnvironmentTable(self, feat):
        self._environmentTable.addFeature(feat)
        self._environmentTable.commitChanges()

    def _getReadyToAddNewFeature(self, table : QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()

        return [feat, table]
