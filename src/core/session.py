# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import QgsProject
from .database import SammoDataBase


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
