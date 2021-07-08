# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (
    QgsWkbTypes,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsProject,
)

DB_NAME = "sammo-boat.gpkg"
LAYER_NAME = "session data"

class SammoDataBase:
    def isDataBaseAvailableInThisDirectory(self, directory):
        return os.path.isfile(self._pathToDataBase(directory))

    @property
    def dbName(self):
        return DB_NAME

    @property
    def _layerName(self, directory):
        return LAYER_NAME

    def createEmptyDataBase(self, directory):
        geom = QgsWkbTypes.Point
        tableName = "emptyTable"
        db = self._pathToDataBase(directory)

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
        db = self._pathToDataBase(directory)
        vlayer = QgsVectorLayer(db, self._layerName())
        if not vlayer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the file " + self._pathToDataBase(),
            )
        else:
            QgsProject.instance().addMapLayer(vlayer)

    def _pathToDataBase(self, directory):
        return os.path.join(directory, DB_NAME)
