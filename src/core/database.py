# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsWkbTypes,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsField
)


class SammoDataBase:
    DB_NAME = "sammo-boat.gpkg"
    LAYER_NAME = "session data"
    ENVIRONMENT_TABLE_NAME = "environment"
    ENVIRONMENT_COMMENT_FIELD_NAME = "commentaire"

    @staticmethod
    def isDataBaseAvailableInThisDirectory(directory):
        return os.path.isfile(SammoDataBase._pathToDataBase(directory))

    def createEmptyDataBase(self, directory):
        db = SammoDataBase._pathToDataBase(directory)

        SammoDataBase._addTableToDataBaseFile(
            db, self._createFieldsForEnvironmentTable(), "environment"
        )

    @staticmethod
    def _addTableToDataBaseFile(db, fields, tableName):
        """
        Create the database and save it as gpkg file

        :param db: path to gpkg file to append to or create
        :param fields: the fields of the table
        :param tableName: the name of the table
        """
        geom = QgsWkbTypes.NoGeometry
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = tableName
        if not os.path.isfile(db):
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteFile
            )
        else:
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteLayer
            )
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

    @staticmethod
    def _pathToDataBase(directory):
        return os.path.join(directory, SammoDataBase.DB_NAME)

    def _createFieldsForEnvironmentTable(self):
        fields = QgsFields()
        fields.append(QgsField("code_leg", QVariant.Int))
        fields.append(self._createFieldShortText("heure"))
        fields.append(self._createFieldShortText("leg_heure"))
        fields.append(self._createFieldShortText("code_trans"))
        fields.append(QgsField("jour", QVariant.Int))
        fields.append(QgsField("mois", QVariant.Int))
        fields.append(QgsField("an", QVariant.Int))
        fields.append(self._createFieldShortText("activite"))
        fields.append(self._createFieldShortText("plateforme"))
        fields.append(QgsField("cap", QVariant.Double))
        fields.append(QgsField("vitesse", QVariant.Double))
        fields.append(QgsField("N observateurs", QVariant.Int))
        fields.append(self._createFieldShortText("obs_babord"))
        fields.append(self._createFieldShortText("obs_tribord"))
        fields.append(QgsField("ebl_de", QVariant.Double))
        fields.append(QgsField("ebl_a", QVariant.Double))
        fields.append(self._createFieldShortText("ebl_intensite"))
        fields.append(QgsField("vent_vrai_direction", QVariant.Double))
        fields.append(QgsField("vent_vrai_force", QVariant.Int))
        fields.append(QgsField("houle_direction", QVariant.Double))
        fields.append(QgsField("houle_hauteur", QVariant.Double))
        fields.append(QgsField("beaufort", QVariant.Int))
        fields.append(QgsField("nebulosite", QVariant.Int))
        fields.append(self._createFieldShortText("cond_generale"))
        fields.append(QgsField("visibilité", QVariant.Double))
        fields.append(self._createFieldShortText(SammoDataBase.ENVIRONMENT_COMMENT_FIELD_NAME))
        fields.append(self._createFieldShortText("Survey"))

        return fields

    def getIdOfLastAddedFeature(self, layer: QgsVectorLayer):
        maxId = -1
        for feature in layer.getFeatures():
            if feature.id() > maxId:
                maxId = feature.id()
            break

        return maxId

    @staticmethod
    def _createFieldShortText(fieldName):
        return QgsField(fieldName, QVariant.String, len=50)

    def loadTable(self, directory, tableName):
        db = self._pathToDataBase(directory)
        return QgsVectorLayer(db, tableName)
