# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField
from qgis.core import (
    QgsWkbTypes,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeatureSink,
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
    def _layerName(self):
        return LAYER_NAME

    def createEmptyDataBase(self, directory):
        db = self._pathToDataBase(directory)

        self.AddTableToDataBaseFile(
            db, self._createFieldsForEnvironmentTable(), "environmentTable"
        )

    def AddTableToDataBaseFile(self, db, fields, tableName):
        """
        Create the database and save it as gpkg file

        :param db: path to gpkg file to append to or create
        :param fields: the fields of the table
        :param tableName: the name of the table
        """
        geom = QgsWkbTypes.Point
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

    def _pathToDataBase(self, directory):
        return os.path.join(directory, DB_NAME)

    def _createFieldsForEnvironmentTable(self):
        fields = QgsFields()
        fields.append(QgsField("code_leg", QVariant.Int))
        fields.append(self._createField_shortText("heure"))
        fields.append(self._createField_shortText("leg_heure"))
        fields.append(self._createField_shortText("code_trans"))
        fields.append(QgsField("jour", QVariant.Int))
        fields.append(QgsField("mois", QVariant.Int))
        fields.append(QgsField("an", QVariant.Int))
        fields.append(self._createField_shortText("activite"))
        fields.append(self._createField_shortText("plateforme"))
        fields.append(QgsField("cap", QVariant.Double))
        fields.append(QgsField("vitesse", QVariant.Double))
        fields.append(QgsField("N observateurs", QVariant.Int))
        fields.append(self._createField_shortText("obs_babord"))
        fields.append(self._createField_shortText("obs_tribord"))
        fields.append(QgsField("ebl_de", QVariant.Double))
        fields.append(QgsField("ebl_a", QVariant.Double))
        fields.append(self._createField_shortText("ebl_intensite"))
        fields.append(QgsField("vent_vrai_direction", QVariant.Double))
        fields.append(QgsField("vent_vrai_force", QVariant.Int))
        fields.append(QgsField("houle_direction", QVariant.Double))
        fields.append(QgsField("houle_hauteur", QVariant.Double))
        fields.append(QgsField("beaufort", QVariant.Int))
        fields.append(QgsField("nebulosite", QVariant.Int))
        fields.append(self._createField_shortText("cond_generale"))
        fields.append(QgsField("visibilité", QVariant.Double))
        fields.append(self._createField_shortText("commentaire"))
        fields.append(self._createField_shortText("Survey"))

        return fields

    def _createField_shortText(self, fieldName):
        return QgsField(fieldName, QVariant.String, len=50)
