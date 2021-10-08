# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
import platform
from datetime import datetime

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import (
    QgsFeature,
    QgsPointXY,
    QgsProject,
    QgsGeometry,
    QgsMapLayer,
    QgsApplication,
    QgsVectorLayer,
    QgsDefaultValue,
    QgsVectorLayerUtils,
    QgsEditorWidgetSetup,
    QgsReferencedRectangle,
    QgsSvgMarkerSymbolLayer,
    QgsCoordinateReferenceSystem,
)

from .icon import path
from .logger import Logger
from .database import (
    SammoDataBase,
    DB_NAME,
    GPS_TABLE,
    SPECIES_TABLE,
    FOLLOWER_TABLE,
    OBSERVER_TABLE,
    SIGHTINGS_TABLE,
    ENVIRONMENT_TABLE,
)

SPECIES_LAYER_NAME = "Species"
ENVIRONMENT_LAYER_NAME = "Effort"
FOLLOWERS_LAYER_NAME = "Followers"
OBSERVERS_LAYER_NAME = "Observers"
SIGHTINGS_LAYER_NAME = "Sightings"


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.lastGpsGeom: QgsGeometry = None

    @property
    def environmentLayer(self) -> QgsVectorLayer:
        return self._layer(ENVIRONMENT_TABLE, ENVIRONMENT_LAYER_NAME)

    @property
    def gpsLayer(self) -> QgsVectorLayer:
        return self._layer(GPS_TABLE)

    @property
    def followerLayer(self) -> QgsVectorLayer:
        return self._layer(FOLLOWER_TABLE, FOLLOWERS_LAYER_NAME)

    @property
    def observerLayer(self) -> QgsVectorLayer:
        return self._layer(OBSERVER_TABLE)

    @property
    def speciesLayer(self) -> QgsVectorLayer:
        return self._layer(SPECIES_TABLE, SPECIES_LAYER_NAME)

    @property
    def sightingsLayer(self) -> QgsVectorLayer:
        return self._layer(SIGHTINGS_TABLE, SIGHTINGS_LAYER_NAME)

    def init(self, directory: str) -> None:
        new = self.db.init(directory)

        # create database if necessary
        if new:
            project = QgsProject()

            # add layers
            worldLayer = SammoSession._initWorldLayer()
            project.addMapLayer(worldLayer)

            gpsLayer = self._initGpsLayer()
            project.addMapLayer(gpsLayer)

            sightingsLayer = self._initSightingsLayer()
            project.addMapLayer(sightingsLayer)

            followerLayer = self._initFollowerLayer()
            project.addMapLayer(followerLayer)

            observerLayer = self._initObserverLayer()
            project.addMapLayer(observerLayer)

            effortLayer = self._initEffortLayer()
            project.addMapLayer(effortLayer)

            speciesLayer = self._initSpeciesLayer()
            project.addMapLayer(speciesLayer)

            # configure project
            crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
            project.setCrs(crs)

            extent = QgsReferencedRectangle(worldLayer.extent(), crs)
            project.viewSettings().setDefaultViewExtent(extent)

            project.setBackgroundColor(QColor(166, 206, 227))

            # save project
            self.db.writeProject(project)

        # read project
        QgsProject.instance().read(self.db.projectUri)

    def onStopSoundRecordingForEvent(
        self,
        isObservation: bool,
        soundFile: str,
        soundStart: str,
        soundEnd: str,
    ):
        if isObservation:
            table = self.sightingsLayer
        else:
            table = self.environmentLayer

        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        if idLastAddedFeature != -1:
            field_idx = table.fields().indexOf("soundFile")
            table.changeAttributeValue(
                idLastAddedFeature, field_idx, soundFile
            )
            field_idx = table.fields().indexOf("soundStart")
            table.changeAttributeValue(
                idLastAddedFeature, field_idx, soundStart
            )
            field_idx = table.fields().indexOf("soundEnd")
            table.changeAttributeValue(idLastAddedFeature, field_idx, soundEnd)
        table.commitChanges()

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self.directory, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def addGps(
        self, longitude: float, latitude: float, hour: int, minu: int, sec: int
    ):
        vlayer = self.gpsLayer
        vlayer.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(vlayer))
        self.lastGpsGeom = QgsGeometry.fromPointXY(
            QgsPointXY(longitude, latitude)
        )
        feature.setGeometry(self.lastGpsGeom)

        now = datetime.now()
        feature.setAttribute("dateTime", now.strftime("%Y-%m-%d %H:%M:%S"))

        gpsNow = datetime(now.year, now.month, now.day, hour, minu, sec)
        feature.setAttribute(
            "gpsDateTime", gpsNow.strftime("%Y-%m-%d %H:%M:%S")
        )

        self._addFeature(feature, vlayer)

    def _layer(self, table: str, name: str = "") -> QgsVectorLayer:
        # return the project layer in priority
        if name and QgsProject.instance().mapLayersByName(name):
            return QgsProject.instance().mapLayersByName(name)[0]

        return QgsVectorLayer(self.db.tableUri(table))

    def _initSightingsLayer(self) -> QgsVectorLayer:
        layer = self.sightingsLayer
        layer.setName(SIGHTINGS_LAYER_NAME)

        # symbology
        symbol = QgsSvgMarkerSymbolLayer(path("observation_symbol.svg"))
        symbol.setSize(6)
        symbol.setFillColor(QColor("#a76dad"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        # side
        idx = layer.fields().indexFromName("side")
        cfg = {}
        cfg["map"] = [
            {"L": "L"},
            {"R": "R"},
            {"B": "B"},
            {"C": "C"},
            {"O": "O"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'R'"))

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"species"',
            "FilterExpression": "",
            "Key": "species",
            "Layer": self.speciesLayer.id(),
            "LayerName": SPECIES_LAYER_NAME,
            "LayerProviderName": "ogr",
            "LayerSource": self.db.tableUri(SPECIES_TABLE),
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "species",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # podSize
        idx = layer.fields().indexFromName("podSize")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("10"))

        # podSizeMin
        idx = layer.fields().indexFromName("podSizeMin")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("5"))

        # podSizeMax
        idx = layer.fields().indexFromName("podSizeMax")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("15"))

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"A": "A"},
            {"I": "I"},
            {"J": "J"},
            {"M": "M"},
            {"I1": "I1"},
            {"I2": "I2"},
            {"I3": "I3"},
            {"I4": "I4"},
            {"NA": "NA"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'A'"))

        # distance
        idx = layer.fields().indexFromName("distance")
        cfg = {
            "AllowNull": False,
            "Max": 20000,
            "Min": 2,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

        # angle
        idx = layer.fields().indexFromName("angle")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

        # direction
        idx = layer.fields().indexFromName("direction")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

        # behaviour
        idx = layer.fields().indexFromName("behaviour")
        cfg = {}
        cfg["map"] = [
            {"ATTRACTION": "ATTRACTION"},
            {"DEPLACEMENT": "DEPLACEMENT"},
            {"FORAGING": "FORAGING"},
            {"FUITE": "FUITE"},
            {"STATIONNAIRE": "STATIONNAIRE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'FORAGING'"))

        # behavGroup
        idx = layer.fields().indexFromName("behavGroup")
        cfg = {}
        cfg["map"] = [
            {"CHASSE": "CHASSE"},
            {"GROUPE_COMPACT": "GROUPE_COMPACT"},
            {"GROUPE_DISPERSE": "GROUPE_DISPERSE"},
            {"MFSA": "MFSA"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'MFSA'"))

        # behavMam
        idx = layer.fields().indexFromName("behavMam")
        cfg = {}
        cfg["map"] = [
            {"ETRAVE": "ETRAVE"},
            {"MILLING": "MILLING"},
            {"NAGE_LENTE": "NAGE_LENTE"},
            {"NAGE_RAPIDE": "NAGE_RAPIDE"},
            {"PLONGE": "PLONGE"},
            {"SAUTE": "SAUTE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'PLONGE'"))

        # behavBird
        idx = layer.fields().indexFromName("behavBird")
        cfg = {}
        cfg["map"] = [
            {"ATTAQUE": "ATTAQUE"},
            {"AVEC_PROIE": "AVEC_PROIE"},
            {"CHAROGNARD": "CHAROGNARD"},
            {"KLEPTO": "KLEPTO"},
            {"PLONGE": "PLONGE"},
            {"SCAVEN_BATEAU": "SCAVEN_BATEAU"},
            {"2_VOL_ALEATOIRE": "2_VOL_ALEATOIRE"},
            {"3_VOL_CIRCULAIRE": "3_VOL_CIRCULAIRE"},
            {"1_VOL_DIRECT": "1_VOL_DIRECT"},
            {"NAGE": "NAGE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'1_VOL_DIRECT'"))

        # behavShip
        idx = layer.fields().indexFromName("behavShip")
        cfg = {}
        cfg["map"] = [
            {"PECHE": "PECHE"},
            {"ROUTE": "ROUTE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'ROUTE'"))

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        return layer

    def _initSpeciesLayer(self) -> QgsVectorLayer:
        layer = self.speciesLayer
        layer.setName(SPECIES_LAYER_NAME)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        return layer

    def _initFollowerLayer(self) -> QgsVectorLayer:
        layer = self.followerLayer
        layer.setName(FOLLOWERS_LAYER_NAME)

        # symbology
        symbol = QgsSvgMarkerSymbolLayer(path("seabird_symbol.svg"))
        symbol.setSize(6)
        symbol.setFillColor(QColor("#e89d34"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        # nFollower
        idx = layer.fields().indexFromName("nFollower")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # podSize
        idx = layer.fields().indexFromName("podSize")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("10"))

        # back
        idx = layer.fields().indexFromName("back")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"observer"',
            "FilterExpression": "",
            "Key": "observer",
            "Layer": self.observerLayer.id(),
            "LayerName": OBSERVERS_LAYER_NAME,
            "LayerProviderName": "ogr",
            "LayerSource": self.db.tableUri(OBSERVER_TABLE),
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "observer",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # fishActivity
        idx = layer.fields().indexFromName("fishActivity")
        cfg = {}
        cfg["map"] = [
            {"FILAGE": "FILAGE"},
            {"VIRAGE": "VIRAGE"},
            {"REJETS": "REJETS"},
            {"EN_PECHE": "EN_PECHE"},
            {"NON_ACTIVE": "NON_ACTIVE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'VIRAGE'"))

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"species"',
            "FilterExpression": "",
            "Key": "species",
            "Layer": self.speciesLayer.id(),
            "LayerName": SPECIES_LAYER_NAME,
            "LayerProviderName": "ogr",
            "LayerSource": self.db.tableUri(SPECIES_TABLE),
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "species",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"A": "A"},
            {"I": "I"},
            {"J": "J"},
            {"M": "M"},
            {"I1": "I1"},
            {"I2": "I2"},
            {"I3": "I3"},
            {"I4": "I4"},
            {"NA": "NA"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'A'"))

        # unlucky
        idx = layer.fields().indexFromName("unlucky")
        cfg = {}
        cfg["map"] = [
            {"MALADE/BLESSE": "MALADE/BLESSE"},
            {"MAZOUTE": "MAZOUTE"},
            {"PRIS_ENGIN_PECHE": "PRIS_ENGIN_PECHE"},
            {"HAMECON": "HAMECON"},
            {"FIL_PECHE": "FIL_PECHE"},
            {"TAG": "TAG"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'TAG'"))

        # dateTime
        idx = layer.fields().indexFromName("dateTime")
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, True)
        layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        return layer

    def _initEffortLayer(self) -> QgsVectorLayer:
        layer = self.environmentLayer
        layer.setName(ENVIRONMENT_LAYER_NAME)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        # status
        idx = layer.fields().indexFromName("status")
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, True)
        layer.setEditFormConfig(form_config)

        # platform
        idx = layer.fields().indexFromName("plateform")
        cfg = {}
        cfg["map"] = [
            {"passerelle": "passerelle"},
            {"pont_sup": "pont_sup"},
            {"pont_inf": "pont_inf"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'pont_sup'"))

        # route type
        idx = layer.fields().indexFromName("routeType")
        cfg = {}
        cfg["map"] = [
            {"prospection": "prospection"},
            {"trawling": "trawling"},
            {"other": "other"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'prospection'"))

        # sea state
        idx = layer.fields().indexFromName("seaState")
        cfg = {
            "AllowNull": False,
            "Max": 13,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("2"))

        # wind direction
        idx = layer.fields().indexFromName("windDirection")
        cfg = {
            "AllowNull": False,
            "Max": 361,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("71"))

        # wind force
        idx = layer.fields().indexFromName("windForce")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("71"))

        # swell direction
        idx = layer.fields().indexFromName("swellDirection")
        cfg = {
            "AllowNull": False,
            "Max": 361,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("165"))

        # swell height
        idx = layer.fields().indexFromName("swellHeight")
        cfg = {
            "AllowNull": False,
            "Max": 20,
            "Min": 0,
            "Precision": 1,
            "Step": 0.5,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0.5"))

        # glare from
        idx = layer.fields().indexFromName("glareFrom")
        cfg = {
            "AllowNull": False,
            "Max": 361,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # glare to
        idx = layer.fields().indexFromName("glareTo")
        cfg = {
            "AllowNull": False,
            "Max": 361,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # glare severity
        idx = layer.fields().indexFromName("glareSever")
        cfg = {}
        cfg["map"] = [
            {"aucun": "aucun"},
            {"faible": "faible"},
            {"moyen": "moyen"},
            {"fort": "fort"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'aucun'"))

        # cloud cover
        idx = layer.fields().indexFromName("cloudCover")
        cfg = {
            "AllowNull": False,
            "Max": 8,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("8"))

        # visibility
        idx = layer.fields().indexFromName("visibility")
        cfg = {}
        cfg["map"] = [
            {"0.5": "0.5"},
            {"1": "1"},
            {"2": "2"},
            {"5": "5"},
            {"10": "10"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0.5"))

        # subjective
        idx = layer.fields().indexFromName("subjective")
        cfg = {}
        cfg["map"] = [
            {"E": "E"},
            {"G": "G"},
            {"M": "M"},
            {"P": "P"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'G'"))

        # n observers
        idx = layer.fields().indexFromName("nObservers")
        cfg = {
            "AllowNull": False,
            "Max": 4,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("2"))

        # camera
        idx = layer.fields().indexFromName("camera")
        cfg = {}
        cfg["map"] = [
            {"ON": "ON"},
            {"OFF": "OFF"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'ON'"))

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        # left/right/center
        for field in ["left", "right", "center"]:
            idx = layer.fields().indexFromName(field)
            cfg = {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": '"observer"',
                "FilterExpression": "",
                "Key": "observer",
                "Layer": self.observerLayer.id(),
                "LayerName": OBSERVERS_LAYER_NAME,
                "LayerProviderName": "ogr",
                "LayerSource": self.db.tableUri(OBSERVER_TABLE),
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "observer",
            }
            setup = QgsEditorWidgetSetup("ValueRelation", cfg)
            layer.setEditorWidgetSetup(idx, setup)

        return layer

    def _initGpsLayer(self) -> QgsVectorLayer:
        gpsLayer = self.gpsLayer
        gpsLayer.setName("GPS")

        symbol = gpsLayer.renderer().symbol()
        symbol.setColor(QColor(219, 30, 42))
        symbol.setSize(2)

        gpsLayer.setAutoRefreshInterval(1000)
        gpsLayer.setAutoRefreshEnabled(True)

        return gpsLayer

    def _initObserverLayer(self) -> QgsVectorLayer:
        layer = self.observerLayer
        layer.setName(OBSERVERS_LAYER_NAME)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        return layer

    @staticmethod
    def sessionDirectory(project: QgsProject) -> str:
        for layer in project.mapLayers().values():
            if layer.type() != QgsMapLayer.VectorLayer:
                continue

            uri = layer.dataProvider().dataSourceUri()
            if DB_NAME in uri:
                return uri.split("|")[0].replace(DB_NAME, "")

        return ""

    @staticmethod
    def _addFeature(feature: QgsFeature, vlayer: QgsVectorLayer) -> None:
        if not vlayer.addFeature(feature):
            Logger.error("addFeature : échec ")
        if not vlayer.commitChanges():
            Logger.error("_addFeatureThreadSafe : échec ")

    @staticmethod
    def _worldMapPath() -> str:
        path = QgsApplication.instance().pkgDataPath()
        if platform.system() == "Windows":
            path = os.path.join(
                path, "resources", "data", "world_map.gpkg|layername=countries"
            )
        else:
            path = os.path.join(
                path,
                "resources",
                "data",
                "world_map.gpkg|layername=countries",
            )
        return path

    @staticmethod
    def _initWorldLayer() -> QgsVectorLayer:
        worldLayer = QgsVectorLayer(SammoSession._worldMapPath(), "World")
        symbol = worldLayer.renderer().symbol()
        symbol.setColor(QColor(178, 223, 138))
        return worldLayer
