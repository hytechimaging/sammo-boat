# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFields,
    QgsWkbTypes,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
)

DB_NAME = "sammo-boat.gpkg"
LAYER_NAME = "session data"
ENVIRONMENT_TABLE_NAME = "environment"
SPECIES_TABLE_NAME = "species"
OBSERVATION_TABLE_NAME = "observations"
FOLLOWER_TABLE_NAME = "followers"
GPS_TABLE_NAME = "gps"


class SammoDataBase:
    def __init__(self):
        self.directory: str = ""

    @property
    def path(self) -> str:
        return os.path.join(self.directory, DB_NAME)

    def projectUri(self, project: str) -> str:
        return f"geopackage:{self.path}?projectName={project}"

    def tableUri(self, table: str) -> str:
        return f"{self.path}|layername={table}"

    def init(self, directory: str) -> bool:
        if SammoDataBase.exist(directory):
            return False

        self.directory = directory

        self._createTable(
            self._createFieldsForEnvironmentTable(),
            ENVIRONMENT_TABLE_NAME,
            QgsWkbTypes.LineString,
        )
        self._createTable(
            self._createFieldsForSpeciesTable(), SPECIES_TABLE_NAME
        )
        self._createTable(
            self._createFieldsForObservationTable(),
            OBSERVATION_TABLE_NAME,
        )
        self._createTable(
            self._createFieldsForFollowerTable(), FOLLOWER_TABLE_NAME
        )
        self._createTable(
            self._createFieldsForGpsTable(),
            GPS_TABLE_NAME,
            QgsWkbTypes.Point,
        )

        return True

    @staticmethod
    def exist(directory: str) -> bool:
        return os.path.isfile(os.path.join(directory, DB_NAME))

    def _createFieldsForEnvironmentTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(self._createFieldShortText("status"))
        fields.append(self._createFieldShortText("plateform"))
        fields.append(self._createFieldShortText("routeType"))
        fields.append(QgsField("courseAverage", QVariant.Int))
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

        fields.append(self._createFieldShortText("fichier_son"))
        fields.append(self._createFieldShortText("sound_start"))
        fields.append(self._createFieldShortText("sound_end"))

        return fields

    @staticmethod
    def getIdOfLastAddedFeature(layer: QgsVectorLayer) -> int:
        maxId = -1
        for feature in layer.getFeatures():
            if feature.id() > maxId:
                maxId = feature.id()

        return maxId

    def _createFieldsForSpeciesTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("code_esp"))
        fields.append(self._createFieldShortText("nom_latin"))
        fields.append(self._createFieldShortText("type"))
        fields.append(self._createFieldShortText("cat_group_size"))
        fields.append(self._createFieldShortText("groupe"))
        fields.append(self._createFieldShortText("Famille"))
        fields.append(self._createFieldShortText("List_sp"))
        fields.append(self._createFieldShortText("liste_especes_potentielles"))
        fields.append(self._createFieldShortText("potential_sp"))
        fields.append(self._createFieldShortText("group_pelgas"))
        fields.append(self._createFieldShortText("nom_commun"))
        fields.append(self._createFieldShortText("nom_anglais"))
        fields.append(self._createFieldShortText("nom_espagnol"))
        fields.append(self._createFieldShortText("phylum_public"))
        fields.append(self._createFieldShortText("classe_public"))
        fields.append(self._createFieldShortText("ordre_public"))
        fields.append(self._createFieldShortText("famille_public"))
        fields.append(self._createFieldShortText("taxon_fr"))
        fields.append(self._createFieldShortText("family_eng"))
        fields.append(self._createFieldShortText("group_eng"))
        fields.append(QgsField("id_public", QVariant.Int))
        fields.append(self._createFieldShortText("LB_NOM_taxref"))
        fields.append(self._createFieldShortText("NOM_VERN_taxref"))
        fields.append(self._createFieldShortText("NOM_VERN_ENG_taxref"))
        fields.append(QgsField("CD_NOM_taxref", QVariant.Int))
        fields.append(QgsField("APHIA_ID_taxref", QVariant.Int))
        fields.append(self._createFieldShortText("REGNE_taxref"))
        fields.append(self._createFieldShortText("PHYLUM_taxref"))
        fields.append(self._createFieldShortText("CLASSE_taxref"))
        fields.append(self._createFieldShortText("ORDRE_taxref"))
        fields.append(self._createFieldShortText("FAMILLE_taxref"))
        fields.append(self._createFieldShortText("R_Caraibes"))

        return fields

    def _createFieldsForObservationTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(QgsField("sightNum", QVariant.Int))
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
        fields.append(self._createFieldShortText("fichier_son"))
        fields.append(self._createFieldShortText("sound_start"))
        fields.append(self._createFieldShortText("sound_end"))

        return fields

    def _createFieldsForFollowerTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("nFollower", QVariant.Int))
        fields.append(self._createFieldShortText("back"))
        fields.append(self._createFieldShortText("dateTime"))
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
        fields.append(QgsField("speed", QVariant.Double))
        fields.append(QgsField("course", QVariant.Int))

        return fields

    def _createTable(self,
        fields: QgsFields, tableName: str, geom=QgsWkbTypes.NoGeometry
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
    def _createFieldShortText(fieldName) -> QgsField:
        return QgsField(fieldName, QVariant.String, len=50)
