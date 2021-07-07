# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from PyQt5.QtWidgets import QMessageBox
from qgis._core import (
    QgsWkbTypes,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsProject,
)

CONST_DB_NAME = "sammo-boat.gpkg"
CONST_LAYER_NAME = "session datas"

class SammoDataBase:
    def isDataBaseAvailableInThisDirectory(self, directory):
        return os.path.isfile(self._getPathToDataBase(directory))

    def getDbName(self):
        return CONST_DB_NAME

    def createEmptyDataBase(self, directory):
        geom = QgsWkbTypes.Point
        tableName = "emptyTable"
        db = self._getPathToDataBase(directory)

        fields = QgsFields()

        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = tableName

        if not os.path.isfile(db):
            opts.actionOnExistingFile = \
                QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            opts.actionOnExistingFile = \
                QgsVectorFileWriter.CreateOrOverwriteLayer

        crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)

        QgsVectorFileWriter.create(
            db,
            fields,
            geom,
            crs,
            QgsCoordinateTransformContext(),
            opts,
            QgsFeatureSink.SinkFlags(),
            None,
            tableName,
        )

    def loadDataBase(self, directory):
        db = self._getPathToDataBase(directory)
        vlayer = QgsVectorLayer(db, self.CONST_LAYER_NAME)
        if not vlayer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the file " + self.CONST_DB_NAME,
            )
        else:
            QgsProject.instance().addMapLayer(vlayer)

    def _getPathToDataBase(self, directory):
        return os.path.join(directory, self.CONST_DB_NAME)
