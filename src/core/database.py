# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

import csv
import os.path
from pathlib import Path

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFields,
    QgsFeature,
    QgsProject,
    QgsWkbTypes,
    QgsApplication,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
)

from .status import StatusCode

DB_NAME = "sammo-boat.gpkg"

GPS_TABLE = "gps"
SPECIES_TABLE = "species"
OBSERVERS_TABLE = "observers"
FOLLOWERS_TABLE = "followers"
SIGHTINGS_TABLE = "sightings"
ENVIRONMENT_TABLE = "environment"
WORLD_TABLE = "world"
BOAT_TABLE = "boat"
SURVEY_TABLE = "survey"
TRANSECT_TABLE = "transect"
STRATE_TABLE = "strate"
PLATEFORM_TABLE = "plateform"


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
            self._createFieldsForEnvironmentTable(),
            ENVIRONMENT_TABLE,
            QgsWkbTypes.Point,
        )
        self._createTable(self._createFieldsForSpeciesTable(), SPECIES_TABLE)
        self._createTable(
            self._fieldsSightings(), SIGHTINGS_TABLE, QgsWkbTypes.Point
        )
        self._createTable(
            self._createFieldsForFollowersTable(),
            FOLLOWERS_TABLE,
            QgsWkbTypes.Point,
        )
        self._createTable(
            self._createFieldsForGpsTable(), GPS_TABLE, QgsWkbTypes.Point
        )

        self._createTable(self._fieldsObserver(), OBSERVERS_TABLE)

        # administrator table
        self._createTable(self._fieldsBoat(), BOAT_TABLE)
        self._populateBoatTable()
        self._createTable(self._fieldsSurvey(), SURVEY_TABLE)
        self._createTable(self._fieldsTransect(), TRANSECT_TABLE)
        self._createTable(self._fieldsStrate(), STRATE_TABLE)
        self._createTable(self._fieldsPlateform(), PLATEFORM_TABLE)
        self._populatePlateformTable()

        self._copyWorldTable()

        return True

    @staticmethod
    def exist(directory: str) -> bool:
        return os.path.isfile(os.path.join(directory, DB_NAME))

    @staticmethod
    def lastFeature(layer: QgsVectorLayer) -> QgsFeature:
        feat = None
        for feature in layer.getFeatures(
            QgsFeatureRequest().addOrderBy("fid", False)
        ):
            if layer.name().casefold() == ENVIRONMENT_TABLE and feature[
                "status"
            ] == StatusCode.display(StatusCode.END):
                continue

            if not feat:
                feat = feature
            elif feature.id() > feat.id():
                feat = feature

        return feat

    def _createFieldsForEnvironmentTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("survey"))
        fields.append(self._createFieldShortText("cycle"))
        fields.append(self._createFieldShortText("session"))
        fields.append(self._createFieldShortText("shipName"))
        fields.append(self._createFieldShortText("computer"))
        fields.append(self._createFieldShortText("left"))
        fields.append(self._createFieldShortText("right"))
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(self._createFieldShortText("plateformId"))
        fields.append(self._createFieldShortText("routeType"))
        fields.append(QgsField("speed", QVariant.Int))
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
        fields.append(self._createFieldShortText("visibility", 3))
        fields.append(QgsField("subjectiveMam", QVariant.String, len=2))
        fields.append(QgsField("subjectiveBirds", QVariant.String, len=2))
        fields.append(QgsField("nObservers", QVariant.Int))
        fields.append(self._createFieldShortText("camera"))
        fields.append(QgsField("comment", QVariant.String, len=200))
        fields.append(self._createFieldShortText("center"))
        fields.append(self._createFieldShortText("transect"))
        fields.append(self._createFieldShortText("strate"))
        fields.append(self._createFieldShortText("length"))
        fields.append(self._createFieldShortText("status", len=5))

        fields.append(self._createFieldShortText("soundFile", len=80))
        fields.append(self._createFieldShortText("soundStart"))
        fields.append(self._createFieldShortText("soundEnd"))
        fields.append(QgsField("validated", QVariant.Bool))
        fields.append(QgsField("effortGroup", QVariant.Int))

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
        fields.append(self._createFieldShortText("sightNum"))
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(self._createFieldShortText("observer"))
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
        fields.append(self._createFieldShortText("behavBird"))
        fields.append(self._createFieldShortText("behavMam"))
        fields.append(self._createFieldShortText("behavShip"))
        fields.append(self._createFieldShortText("behavGroup"))
        fields.append(QgsField("comment", QVariant.String, len=200))
        fields.append(self._createFieldShortText("soundFile", len=80))
        fields.append(self._createFieldShortText("soundStart"))
        fields.append(self._createFieldShortText("soundEnd"))
        fields.append(QgsField("validated", QVariant.Bool))
        fields.append(QgsField("effortGroup", QVariant.Int))

        return fields

    def _createFieldsForFollowersTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("nFollower", QVariant.Int))
        fields.append(self._createFieldShortText("back"))
        fields.append(QgsField("dateTime", QVariant.DateTime))
        fields.append(self._createFieldShortText("fishActivity"))
        fields.append(self._createFieldShortText("species"))
        fields.append(QgsField("podSize", QVariant.Int))
        fields.append(self._createFieldShortText("age"))
        fields.append(self._createFieldShortText("unlucky"))
        fields.append(QgsField("comment", QVariant.String, len=200))
        fields.append(self._createFieldShortText("soundFile", len=80))
        fields.append(self._createFieldShortText("soundStart"))
        fields.append(self._createFieldShortText("soundEnd"))
        fields.append(QgsField("validated", QVariant.Bool))
        fields.append(QgsField("effortGroup", QVariant.Int))

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

    def _fieldsBoat(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("name"))
        return fields

    def _populateBoatTable(self) -> None:
        boatLyr = QgsVectorLayer(self.tableUri(BOAT_TABLE), "boat", "ogr")
        file = Path(__file__).parent.parent.parent / "data" / "boat.csv"
        boats = []
        if file.exists():
            with open(file.as_posix()) as f:
                boats = [
                    {k: v for k, v in row.items()} for row in csv.DictReader(f)
                ]
        boatLyr.startEditing()
        for boatAttr in boats:
            ft = QgsFeature(boatLyr.fields())
            for k, v in boatAttr.items():
                ft[k] = v
            boatLyr.addFeature(ft)
        boatLyr.commitChanges()

    def _fieldsSurvey(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("region"))
        fields.append(self._createFieldShortText("survey"))
        fields.append(self._createFieldShortText("computer"))
        fields.append(self._createFieldShortText("shipName"))
        fields.append(self._createFieldShortText("cycle"))
        fields.append(self._createFieldShortText("session"))

        return fields

    def _fieldsTransect(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("transect"))
        fields.append(self._createFieldShortText("strate"))
        fields.append(QgsField("length", QVariant.Int))

        return fields

    def _fieldsStrate(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("state"))
        fields.append(self._createFieldShortText("subRegion"))
        fields.append(self._createFieldShortText("region"))

        return fields

    def _fieldsPlateform(self) -> QgsFields:
        fields = QgsFields()
        fields.append(self._createFieldShortText("ship"))
        fields.append(self._createFieldShortText("plateform"))
        fields.append(QgsField("plateformHeight", QVariant.Double))

        return fields

    def _populatePlateformTable(self) -> None:
        plateformLyr = QgsVectorLayer(
            self.tableUri(PLATEFORM_TABLE), "plateform", "ogr"
        )
        file = Path(__file__).parent.parent.parent / "data" / "plateform.csv"
        plateforms = []
        if file.exists():
            with open(file.as_posix()) as f:
                plateforms = [
                    {
                        k: (float(v) if k == "plateformHeight" else v)
                        for k, v in row.items()
                    }
                    for row in csv.DictReader(f)
                ]
        plateformLyr.startEditing()
        for plateformAttr in plateforms:
            ft = QgsFeature(plateformLyr.fields())
            for k, v in plateformAttr.items():
                ft[k] = v
            plateformLyr.addFeature(ft)
        plateformLyr.commitChanges()

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

    def _copyWorldTable(self) -> None:
        """
        Copy world table from qgis data into gpkg file
        """
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = WORLD_TABLE
        opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        layer = QgsVectorLayer(self._worldMapPath(), "World")
        QgsVectorFileWriter.writeAsVectorFormatV2(
            layer, self.path, QgsCoordinateTransformContext(), opts
        )

    @staticmethod
    def _worldMapPath() -> str:
        return (
            Path(QgsApplication.instance().pkgDataPath())
            / "resources"
            / "data"
            / "world_map.gpkg"
        ).as_posix() + "|layername=countries"
