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
        pass

    def IsDataBaseAvailableInThisDirectory(self, directory):
        return self.db.IsDataBaseAvailableInThisDirectory(directory)

    def CreateEmptyDataBase(self, directory):
        self.db.CreateEmptyDataBase(directory)

    def LoadDataBase(self, directory):
        self.db.LoadDataBase(directory)

    def IsDataBaseLayerExistsInCurrentProject(self):
        db_layers = QgsProject.instance().mapLayersByName(
            SammoDataBase.CONST_LAYER_NAME
        )
        return len(db_layers) != 0
