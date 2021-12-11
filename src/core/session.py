# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
import platform

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsSettings,
    QgsApplication,
    QgsVectorLayer,
    QgsReferencedRectangle,
    QgsCoordinateReferenceSystem,
)

from .database import (
    SammoDataBase,
    DB_NAME,
)
from .layers import (
    SammoFollowersLayer,
    SammoObserversLayer,
    SammoSpeciesLayer,
    SammoEnvironmentLayer,
    SammoSightingsLayer,
    SammoGpsLayer,
)
from .sound_recording_controller import RecordType


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()

        self._gpsLayer: SammoGpsLayer
        self._speciesLayer: SammoSpeciesLayer
        self._followersLayer: SammoFollowersLayer
        self._observersLayer: SammoObserversLayer
        self._sightingsLayer: SammoSightingsLayer
        self._environmentLayer: SammoEnvironmentLayer

    @property
    def environmentLayer(self) -> QgsVectorLayer:
        return self._environmentLayer.layer

    @property
    def gpsLayer(self) -> QgsVectorLayer:
        return self._gpsLayer.layer

    @property
    def followersLayer(self) -> QgsVectorLayer:
        return self._followersLayer.layer

    @property
    def observersLayer(self) -> QgsVectorLayer:
        return self._observersLayer.layer

    @property
    def speciesLayer(self) -> QgsVectorLayer:
        return self._speciesLayer.layer

    @property
    def sightingsLayer(self) -> QgsVectorLayer:
        return self._sightingsLayer.layer

    def init(self, directory: str) -> None:
        new = self.db.init(directory)

        # create database if necessary
        if new:
            project = QgsProject()

            # add layers
            worldLayer = SammoSession._initWorldLayer()
            project.addMapLayer(worldLayer)

            self._gpsLayer = SammoGpsLayer(self.db)
            self._gpsLayer.addToProject(project)

            self._speciesLayer = SammoSpeciesLayer(self.db)
            self._speciesLayer.addToProject(project)

            self._sightingsLayer = SammoSightingsLayer(self.db)
            self._sightingsLayer.addToProject(project)

            self._observersLayer = SammoObserversLayer(self.db)
            self._observersLayer.addToProject(project)

            self._followersLayer = SammoFollowersLayer(
                self.db, self._observersLayer, self._speciesLayer
            )
            self._followersLayer.addToProject(project)

            self._environmentLayer = SammoEnvironmentLayer(
                self.db, self._observersLayer
            )
            self._environmentLayer.addToProject(project)

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
        if recordType == RecordType.ENVIRONMENT:
            table = self.environmentLayer
        elif recordType == RecordType.SIGHTINGS:
            table = self.sightingsLayer
        else:
            table = self.followersLayer

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

    def addGps(
        self, longitude: float, latitude: float, hour: int, minu: int, sec: int
    ):
        self._gpsLayer.add(longitude, latitude, hour, minu, sec)

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
