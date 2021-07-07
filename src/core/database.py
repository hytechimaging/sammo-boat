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


class SammoDataBase:
    CONST_DB_NAME = "sammo-boat.gpkg"
    CONST_LAYER_NAME = "session datas"

    def __init__(self):
        pass

    def isDataBaseAvailableInThisDirectory(self, directory):
        return os.path.isfile(directory + "/" + self.CONST_DB_NAME)

    def createEmptyDataBase(self, directory):
        geom = QgsWkbTypes.Point
        tableName = "emptyTable"
        db = directory + "/" + self.CONST_DB_NAME

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
        db = directory + "/" + self.CONST_DB_NAME
        vlayer = QgsVectorLayer(db, self.CONST_LAYER_NAME)
        if not vlayer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the file " + self.CONST_DB_NAME,
            )
        else:
            QgsProject.instance().addMapLayer(vlayer)
