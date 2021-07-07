# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis._core import QgsProject
from .database import SammoDataBase


class QgsMapLayerRegistry:
    pass


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.isDbOpened = False
        self.directoryPath = None
        pass

    def isDataBaseAvailable(self, directory):
        return self.db.isDataBaseAvailableInThisDirectory(directory)

    def createEmptyDataBase(self, directory):
        self.db.createEmptyDataBase(directory)

    def setDirectoryPath(self, directory):
        self.directoryPath = directory

    def loadDataBase(self):
        self.db.loadDataBase(self.directoryPath)

    def isDataBaseLayerExistsInCurrentProject(self):
        db_layers = QgsProject.instance().mapLayersByName(
            SammoDataBase.CONST_LAYER_NAME
        )
        return len(db_layers) != 0
