# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .database import SammoDataBase
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayerUtils


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.isDbOpened = False
        self.directoryPath = None

    @staticmethod
    def isDataBaseAvailable(directory):
        return SammoDataBase.isDataBaseAvailableInThisDirectory(directory)

    def createEmptyDataBase(self, directory):
        self.db.createEmptyDataBase(directory)

    def loadTable(self, tableName):
        return self.db.loadTable(self.directoryPath, tableName)

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(SammoDataBase.ENVIRONMENT_TABLE_NAME)

    def addNewFeatureToEnvironmentTable(self, table, feat):
        table.addFeature(feat)
        table.commitChanges()

    def _getReadyToAddNewFeature(self, tableName):
        table = self.loadTable(tableName)
        if not table.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName
            )
            return

        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()

        return [feat, table]
