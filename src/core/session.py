# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
import platform
from datetime import datetime

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.gui import QgsMapCanvas
from qgis.core import (
    QgsPoint,
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
    QgsCoordinateReferenceSystem,
)

from .logger import Logger
from .database import (
    SammoDataBase,
    DB_NAME,
    GPS_TABLE,
    FOLLOWER_TABLE,
    OBSERVER_TABLE,
    ENVIRONMENT_TABLE,
)

FOLLOWERS_LAYER_NAME = "Followers"
OBSERVERS_LAYER_NAME = "Observers"
ENVIRONMENT_LAYER_NAME = "Effort"


class SammoSession:
    def __init__(self, mapCanvas: QgsMapCanvas):
        self.mapCanvas: QgsMapCanvas = mapCanvas
        self.db = SammoDataBase()
        self._gpsLocationsDuringEffort = []
        self._lastEnvironmentFeature: QgsFeature = None

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

    def init(self, directory: str) -> None:
        extent = self.mapCanvas.projectExtent()
        new = self.db.init(directory)

        # create database if necessary
        if new:
            project = QgsProject()

            # add layers
            worldLayer = SammoSession._initWorldLayer()
            project.addMapLayer(worldLayer)

            gpsLayer = self._initGpsLayer()
            project.addMapLayer(gpsLayer)

            observerLayer = self._initObserverLayer()
            project.addMapLayer(observerLayer, False)

            effortLayer = self._initEffortLayer()
            project.addMapLayer(effortLayer)

            followerLayer = self._initFollowerLayer()
            project.addMapLayer(followerLayer, False)

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
            table = self.observationLayer
        else:
            table = self.environmentLayer

        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(table)
        field_idx = table.fields().indexOf("sound_file")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundFile)
        field_idx = table.fields().indexOf("sound_start")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundStart)
        field_idx = table.fields().indexOf("sound_end")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundEnd)
        table.commitChanges()

    def onStopTransect(self):
        if 0 == len(self._gpsLocationsDuringEffort):
            return
        vlayer = self.environmentLayer
        vlayer.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(vlayer)
        vlayer.changeGeometry(
            idLastAddedFeature,
            QgsGeometry.fromPolyline(self._gpsLocationsDuringEffort),
        )
        vlayer.commitChanges()

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self.directory, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def getReadyToAddNewFeatureToFollowerTable(self):
        layer = self.followerLayer
        return self._getReadyToAddNewFeature(layer), layer

    def getReadyToAddNewFeatureToEnvironmentTable(
        self, status: str
    ) -> (QgsFeature, QgsVectorLayer):
        layer = self.environmentLayer
        feat = self._getReadyToAddNewFeature(layer)

        if self._lastEnvironmentFeature:
            feat = self.copyEnvironmentFeature(self._lastEnvironmentFeature)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feat["status"] = status
        return feat, layer

    def addEnvironment(self, feature: QgsFeature) -> None:
        vlayer = self.environmentLayer
        vlayer.startEditing()
        self._addFeature(feature, vlayer)
        # self._lastEnvironmentFeature = self.copyEnvironmentFeature(feature)
        # self._gpsLocationsDuringEffort = []

    def copyEnvironmentFeature(self, feat: QgsFeature) -> QgsFeature:
        copyFeature = QgsVectorLayerUtils.createFeature(self._environmentTable)
        for field in feat.fields():
            copyFeature[field.name()] = feat[field.name()]
        return copyFeature

    def addFollower(self, feature: QgsFeature):
        self._addFeature(feature, self.followerLayer)

    def getReadyToAddNewFeatureToObservationTable(
        self,
    ) -> (QgsFeature, QgsVectorLayer):
        (
            feat,
            table,
        ) = self._getReadyToAddNewFeature(self._observationTable)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return feat, table

    def addObservation(self, feature: QgsFeature):
        self._addFeature(feature, self._observationTable)

    def addGps(
        self, longitude: float, latitude: float, formattedDateTime: str
    ):
        vlayer = self.gpsLayer
        vlayer.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(vlayer))
        point = QgsPointXY(longitude, latitude)
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        feature.setAttribute("dateTime", formattedDateTime)

        self._addFeature(feature, vlayer)
        self._gpsLocationsDuringEffort.append(QgsPoint(longitude, latitude))

    def _layer(self, table: str, name: str = "") -> QgsVectorLayer:
        # return the project layer in priority
        if name and QgsProject.instance().mapLayersByName(name):
            return QgsProject.instance().mapLayersByName(name)[0]

        return QgsVectorLayer(self.db.tableUri(table))

    def _initFollowerLayer(self) -> QgsVectorLayer:
        layer = self.followerLayer
        layer.setName(FOLLOWERS_LAYER_NAME)

        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        return layer

    def _initEffortLayer(self) -> QgsVectorLayer:
        layer = self.environmentLayer
        layer.setName(ENVIRONMENT_LAYER_NAME)

        symbol = layer.renderer().symbol()
        symbol.setColor(QColor(219, 30, 42))

        layer.setAutoRefreshInterval(1000)
        layer.setAutoRefreshEnabled(True)

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

        # sound_file
        idx = layer.fields().indexFromName("sound_file")
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, True)
        layer.setEditFormConfig(form_config)

        # sound_start
        idx = layer.fields().indexFromName("sound_start")
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, True)
        layer.setEditFormConfig(form_config)

        # sound_end
        idx = layer.fields().indexFromName("sound_end")
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, True)
        layer.setEditFormConfig(form_config)

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
    def _getReadyToAddNewFeature(
        layer: QgsVectorLayer,
    ) -> (QgsFeature, QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(layer)
        layer.startEditing()
        return feat

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
