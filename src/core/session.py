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
    QgsSettings,
    QgsApplication,
    QgsVectorLayer,
    QgsDefaultValue,
    QgsVectorLayerUtils,
    QgsFieldConstraints,
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
from .sound_recording_controller import RecordType

SPECIES_LAYER_NAME = "Species"
ENVIRONMENT_LAYER_NAME = "Effort"
FOLLOWERS_LAYER_NAME = "Followers"
OBSERVERS_LAYER_NAME = "Observers"
SIGHTINGS_LAYER_NAME = "Sightings"


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.lastGpsGeom: QgsGeometry = None
        self._cacheAttr = dict()

    @property
    def cacheAttr(self) -> dict:
        return self._cacheAttr

    @cacheAttr.setter
    def cacheAttr(self, key, value):
        self._cacheAttr[key] = value

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

            speciesLayer = self._initSpeciesLayer()
            project.addMapLayer(speciesLayer)

            sightingsLayer = self._initSightingsLayer()
            project.addMapLayer(sightingsLayer)

            followerLayer = self._initFollowerLayer()
            project.addMapLayer(followerLayer)

            observerLayer = self._initObserverLayer()
            project.addMapLayer(observerLayer)

            effortLayer = self._initEffortLayer()
            project.addMapLayer(effortLayer)

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
        QgsSettings().setValue("qgis/enableMacros", "SessionOnly")

    def onStopSoundRecordingForEvent(
        self,
        recordType: RecordType,
        soundFile: str,
        soundStart: str,
        soundEnd: str,
    ):
        if recordType == RecordType.OBSERVATION:
            table = self.sightingsLayer
        elif recordType == RecordType.ENVIRONMENT:
            table = self.environmentLayer
        elif recordType == RecordType.FOLLOWERS:
            table = self.followerLayer

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
            {"L (portside)": "L (portside)"},
            {"R (starboard)": "R (starboard)"},
            {"C (center)": "C (center)"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(
            idx, QgsDefaultValue("'R (starboard)'")
        )

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                    ),
                    'fid'
                ) != 0,
                True,
                False
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

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
        layer.setConstraintExpression(
            idx,
            """
            if(
                "podSizeMax" and "podSizeMin",
                "podSizeMin" <=  "podSize" and  "podSize" <= "podSizeMax",
                True
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # podSizeMin
        idx = layer.fields().indexFromName("podSizeMin")
        cfg = {
            "AllowNull": True,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("5"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                "podSizeMax" and "podSizeMin",
                "podSizeMin" <=  "podSizeMax",
                "podSizeMax" is NULL and "podSizeMin" is NULL
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # podSizeMax
        idx = layer.fields().indexFromName("podSizeMax")
        cfg = {
            "AllowNull": True,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("15"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                "podSizeMax" and "podSizeMin",
                "podSizeMin" <=  "podSizeMax",
                "podSizeMax" is NULL and "podSizeMin" is NULL
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
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
            "AllowNull": True,
            "Max": 20000,
            "Min": 0,
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
            "AllowNull": True,
            "Max": 360,
            "Min": 0,
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
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"attracting": "attracting"},
            {"moving": "moving"},
            {"foraging": "foraging"},
            {"escape": "escape"},
            {"stationary": "stationary"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'foraging'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                array_contains(
                    array('Marine Mammal','Seabird','Ship'),
                    attribute(
                        get_feature(
                            layer_property('Species','id'),
                            'species',
                            attribute('species')
                        ),
                        'taxon'
                    )
                ),
                "behaviour" is not NULL,
                True
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # behavGroup
        idx = layer.fields().indexFromName("behavGroup")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"feeding_agregation": "feeding_agregation"},
            {"MFSA": "MFSA"},
            {"compact_group": "compact_group"},
            {"scattered_group": "scattered_group"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'MFSA'"))

        # behavMam
        idx = layer.fields().indexFromName("behavMam")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"bow": "bow"},
            {"milling": "milling"},
            {"fast_swimming": "fast_swimming"},
            {"slow_swimming": "slow_swimming"},
            {"diving": "diving"},
            {"breaching": "breaching"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'diving'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Marine Mammal',
                "behavMam" is not NULL,
                True
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # behavBird
        idx = layer.fields().indexFromName("behavBird")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"attaking": "attaking"},
            {"with_prey": "with_prey"},
            {"scavenger": "scavenger"},
            {"klepto": "klepto"},
            {"diving": "diving"},
            {"follow_boat": "follow_boat"},
            {"random_flight": "random_flight"},
            {"circular_flight": "circular_flight"},
            {"direct_flight": "direct_flight"},
            {"swimming": "swimming"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(
            idx, QgsDefaultValue("'direct_flight'")
        )
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Seabird',
                "behavBird" is not NULL,
                True
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # behavShip
        idx = layer.fields().indexFromName("behavShip")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"fishing": "fishing"},
            {"go_ahead": "go_ahead"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'go_ahead'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Ship',
                "behavShip" is not NULL,
                True
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field != "dateTime":
                setup = QgsEditorWidgetSetup("Hidden", {})
                layer.setEditorWidgetSetup(idx, setup)
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        form_config = layer.editFormConfig()
        form_config.setInitCode(
            """
from qgis.PyQt.QtWidgets import QLineEdit, QComboBox

def my_form_open(dialog, layer, feature):
    behaviour = dialog.findChild(QComboBox, "behaviour")
    behavMam = dialog.findChild(QComboBox, "behavMam")
    behavBird = dialog.findChild(QComboBox, "behavBird")
    behavShip = dialog.findChild(QComboBox, "behavShip")
    def updateBehav():
        behaviour.currentIndexChanged.emit(behaviour.currentIndex())
        behavMam.currentIndexChanged.emit(behavMam.currentIndex())
        behavBird.currentIndexChanged.emit(behavBird.currentIndex())
        behavShip.currentIndexChanged.emit(behavShip.currentIndex())

    species = dialog.findChild(QLineEdit, "species")
    species.valueChanged.connect(updateBehav)
            """
        )
        form_config.setInitFunction("my_form_open")
        form_config.setInitCodeSource(2)
        layer.setEditFormConfig(form_config)

        layer = self.reuseLastValues(layer)

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
            {"up_net": "up_net"},
            {"net_down": "net_down"},
            {"discard": "discard"},
            {"hauling": "hauling"},
            {"NON_ACTIVE": "NON_ACTIVE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'net_down'"))

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                    ),
                    'fid'
                ) != 0,
                True,
                False
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
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
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"wounded": "wounded"},
            {"oiled": "oiled"},
            {"stuck_fishing_device": "stuck_fishing_device"},
            {"hook": "hook"},
            {"fish_string": "fish_string"},
            {"tag": "tag"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(
            idx, QgsDefaultValue("'{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}'")
        )

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field != "dateTime":
                setup = QgsEditorWidgetSetup("Hidden", {})
                layer.setEditorWidgetSetup(idx, setup)
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        layer = self.reuseLastValues(layer)

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
        cfg = {}
        cfg["map"] = [{"B": "B"}, {"A": "A"}, {"E": "E"}]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'B'"))

        # platform
        idx = layer.fields().indexFromName("plateform")
        cfg = {}
        cfg["map"] = [
            {"bridge": "bridge"},
            {"upper_deck": "upper_deck"},
            {"deck": "deck"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'upper_deck'"))

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
            "Max": 360,
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
            "Max": 360,
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
            "Max": 360,
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
            "Max": 360,
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
            {"none": "none"},
            {"slight": "slight"},
            {"moderate": "moderate"},
            {"strong": "strong"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'none'"))

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
        cfg["map"] = [{"E": "E"}, {"G": "G"}, {"M": "M"}, {"P": "P"}]
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
        cfg["map"] = [{"ON": "ON"}, {"OFF": "OFF"}]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'ON'"))

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field != "dateTime":
                setup = QgsEditorWidgetSetup("Hidden", {})
                layer.setEditorWidgetSetup(idx, setup)
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
                "AllowNull": True,
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

        layer = self.reuseLastValues(layer)

        form_config = layer.editFormConfig()
        form_config.setInitCode(
            """
from qgis.PyQt.QtWidgets import QSpinBox, QComboBox

def my_form_open(dialog, layer, feature):
    glareFrom = dialog.findChild(QSpinBox, "glareFrom")
    glareTo = dialog.findChild(QSpinBox, "glareTo")
    def updateGlareDir(idx):
        if idx:
            glareFrom.setEnabled(True)
            glareTo.setEnabled(True)
            return
        glareFrom.setValue(0)
        glareTo.setValue(0)
        glareFrom.setEnabled(False)
        glareTo.setEnabled(False)

    glareSever = dialog.findChild(QComboBox, "glareSever")
    updateGlareDir(glareSever.currentIndex())
    glareSever.currentIndexChanged.connect(updateGlareDir)
            """
        )
        form_config.setInitFunction("my_form_open")
        form_config.setInitCodeSource(2)
        layer.setEditFormConfig(form_config)

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
    def reuseLastValues(layer: QgsVectorLayer) -> QgsVectorLayer:
        for idx, field in enumerate(layer.fields()):
            form_config = layer.editFormConfig()
            if field.name() in ["fid", "dateTime"] or form_config.readOnly(
                idx
            ):
                continue
            form_config.setReuseLastValue(idx, True)
            layer.setEditFormConfig(form_config)
        return layer

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
                path, "resources", "data", "world_map.gpkg|layername=countries"
            )
        return path

    @staticmethod
    def _initWorldLayer() -> QgsVectorLayer:
        worldLayer = QgsVectorLayer(SammoSession._worldMapPath(), "World")
        symbol = worldLayer.renderer().symbol()
        symbol.setColor(QColor(178, 223, 138))
        return worldLayer
