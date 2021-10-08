# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFields,
    QgsProject,
    QgsWkbTypes,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
)

DB_NAME = "sammo-boat.gpkg"

GPS_TABLE = "gps"
SPECIES_TABLE = "species"
OBSERVER_TABLE = "observer"
FOLLOWER_TABLE = "followers"
SIGHTINGS_TABLE = "sightings"
ENVIRONMENT_TABLE = "environment"


class SammoDataBase:
    def __init__(self):
        self.directory: str = ""

    @property
    def path(self) -> str:
        return os.path.join(self.directory, DB_NAME)

    @property
    def projectUri(self) -> str:
        return f"geopackage:{self.path}?projectName=project"

    def tableUri(self, table: str) -> str:
        return f"{self.path}|layername={table}"

    def writeProject(self, project: QgsProject) -> None:
        project.write(self.projectUri)

    def init(self, directory: str) -> bool:
        self.directory = directory

        if SammoDataBase.exist(directory):
            return False

        self._createTable(
            self._createFieldsForEnvironmentTable(), ENVIRONMENT_TABLE
        )
        self._createTable(self._createFieldsForSpeciesTable(), SPECIES_TABLE)
        self._createTable(
            self._fieldsSightings(), SIGHTINGS_TABLE, QgsWkbTypes.Point
        )
        self._createTable(
            self._createFieldsForFollowerTable(),
            FOLLOWER_TABLE,
            QgsWkbTypes.Point,
        )
        self._createTable(
            self._createFieldsForGpsTable(),
            GPS_TABLE,
            QgsWkbTypes.Point,
        )

        self._createTable(self._fieldsObserver(), OBSERVER_TABLE)

        return True

    @staticmethod
    def exist(directory: str) -> bool:
        return os.path.isfile(os.path.join(directory, DB_NAME))

    @staticmethod
    def getIdOfLastAddedFeature(layer: QgsVectorLayer) -> int:
        maxId = -1
        for feature in layer.getFeatures():
            if feature.id() > maxId:
                maxId = feature.id()

        return maxId

    def _createFieldsForEnvironmentTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(self._createFieldShortText("status"))
        fields.append(self._createFieldShortText("plateform"))
        fields.append(self._createFieldShortText("routeType"))
        fields.append(QgsField("seaState", QVariant.Int))
        fields.append(QgsField("windDirection", QVariant.Int))
        fields.append(QgsField("windForce", QVariant.Int))
        fields.append(QgsField("swellDirection", QVariant.Int))
        fields.append(QgsField("swellHeight", QVariant.Double))
        fields.append(QgsField("glareFrom", QVariant.Int))
        fields.append(QgsField("glareTo", QVariant.Int))
        fields.append(self._createFieldShortText("glareSever"))
        fields.append(QgsField("cloudCover", QVariant.Int))
        fields.append(QgsField("visibility", QVariant.Int))
        fields.append(QgsField("subjective", QVariant.String, len=1))
        fields.append(QgsField("nObservers", QVariant.Int))
        fields.append(self._createFieldShortText("camera"))
        fields.append(QgsField("comment", QVariant.String, len=200))
        fields.append(self._createFieldShortText("left"))
        fields.append(self._createFieldShortText("right"))
        fields.append(self._createFieldShortText("center"))

        fields.append(self._createFieldShortText("soundFile"))
        fields.append(self._createFieldShortText("soundStart"))
        fields.append(self._createFieldShortText("soundEnd"))

        return fields

    def _createFieldsForSpeciesTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("species"))
        fields.append(self._createFieldShortText("commonName"))
        fields.append(self._createFieldShortText("latinName"))
        fields.append(self._createFieldShortText("groupName"))
        fields.append(self._createFieldShortText("family"))
        fields.append(self._createFieldShortText("taxon"))
        return fields

    def _fieldsSightings(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        # fields.append(QgsField("sightNum", QVariant.Int))  # fid
        fields.append(self._createFieldShortText("side"))
        fields.append(self._createFieldShortText("species"))
        fields.append(QgsField("podSize", QVariant.Int))
        fields.append(QgsField("podSizeMin", QVariant.Int))
        fields.append(QgsField("podSizeMax", QVariant.Int))
        fields.append(self._createFieldShortText("age"))
        fields.append(QgsField("distance", QVariant.Int))
        fields.append(QgsField("angle", QVariant.Int))
        fields.append(QgsField("direction", QVariant.Int))
        fields.append(self._createFieldShortText("behaviour"))
        fields.append(self._createFieldShortText("behavGroup"))
        fields.append(self._createFieldShortText("behavMam"))
        fields.append(self._createFieldShortText("behavBird"))
        fields.append(self._createFieldShortText("behavShip"))
        fields.append(QgsField("comment", QVariant.String, len=200))
        fields.append(self._createFieldShortText("soundFile"))
        fields.append(self._createFieldShortText("soundStart"))
        fields.append(self._createFieldShortText("soundEnd"))

        return fields

    def _createFieldsForFollowerTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(QgsField("nFollower", QVariant.Int))
        fields.append(self._createFieldShortText("back"))
        fields.append(self._createFieldShortText("fishActivity"))
        fields.append(self._createFieldShortText("species"))
        fields.append(QgsField("podSize", QVariant.Int))
        fields.append(self._createFieldShortText("age"))
        fields.append(self._createFieldShortText("unlucky"))
        fields.append(QgsField("comment", QVariant.String, len=200))

        return fields

    def _createFieldsForGpsTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(QgsField("gpsDateTime", QVariant.DateTime))
        fields.append(QgsField("speed", QVariant.Double))
        fields.append(QgsField("course", QVariant.Int))

        return fields

    def _fieldsObserver(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("observer", 4))
        fields.append(self._createFieldShortText("firstName"))
        fields.append(self._createFieldShortText("lastName"))
        fields.append(self._createFieldShortText("organization"))
        fields.append(self._createFieldShortText("contact"))

        return fields

    def _createTable(
        self, fields: QgsFields, tableName: str, geom=QgsWkbTypes.NoGeometry
    ) -> None:
        """
        Create the database and save it as gpkg file

        :param fields: the fields of the table
        :param tableName: the name of the table
        """
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = tableName
        if not os.path.isfile(self.path):
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteFile
            )
        else:
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteLayer
            )
        crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        QgsVectorFileWriter.create(
            self.path,
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
    def _createFieldShortText(fieldName, len=50) -> QgsField:
        return QgsField(fieldName, QVariant.String, len=len)
