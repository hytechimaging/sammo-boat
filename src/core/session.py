# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import pathlib
from shutil import copy

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsSettings,
    QgsExpression,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsVectorLayerUtils,
    QgsReferencedRectangle,
    QgsCoordinateReferenceSystem,
)

from . import utils
from .database import (
    DB_NAME,
    SammoDataBase,
)
from .layers import (
    SammoGpsLayer,
    SammoWorldLayer,
    SammoSpeciesLayer,
    SammoFollowersLayer,
    SammoObserversLayer,
    SammoSightingsLayer,
    SammoEnvironmentLayer,
)
from .sound_recording_controller import RecordType


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()

        self._gpsLayer: SammoGpsLayer = None
        self._worldLayer: SammoWorldLayer = None
        self._speciesLayer: SammoSpeciesLayer = None
        self._followersLayer: SammoFollowersLayer = None
        self._observersLayer: SammoObserversLayer = None
        self._sightingsLayer: SammoSightingsLayer = None
        self._environmentLayer: SammoEnvironmentLayer = None

    @property
    def environmentLayer(self) -> QgsVectorLayer:
        if self._environmentLayer:
            return self._environmentLayer.layer
        return None

    @property
    def gpsLayer(self) -> QgsVectorLayer:
        return self._gpsLayer.layer

    @property
    def followersLayer(self) -> QgsVectorLayer:
        if self._followersLayer:
            return self._followersLayer.layer
        return None

    @property
    def observersLayer(self) -> QgsVectorLayer:
        return self._observersLayer.layer

    @property
    def speciesLayer(self) -> QgsVectorLayer:
        return self._speciesLayer.layer

    @property
    def sightingsLayer(self) -> QgsVectorLayer:
        if self._sightingsLayer:
            return self._sightingsLayer.layer
        return None

    @property
    def allLayers(self) -> list[QgsVectorLayer]:
        return [
            self.environmentLayer,
            self.gpsLayer,
            self.followersLayer,
            self.observersLayer,
            self.speciesLayer,
            self.sightingsLayer,
        ]

    @property
    def wavFiles(self) -> list[str]:
        return list(pathlib.Path(self.db.directory).glob("*.wav"))

    def init(self, directory: str, load: bool = True) -> None:
        new = self.db.init(directory)

        self._worldLayer = SammoWorldLayer()
        self._gpsLayer = SammoGpsLayer(self.db)
        self._speciesLayer = SammoSpeciesLayer(self.db)
        self._sightingsLayer = SammoSightingsLayer(self.db)
        self._observersLayer = SammoObserversLayer(self.db)
        self._followersLayer = SammoFollowersLayer(
            self.db, self._observersLayer, self._speciesLayer
        )
        self._environmentLayer = SammoEnvironmentLayer(
            self.db, self._observersLayer
        )

        # create database if necessary
        if new:
            project = QgsProject()

            # add layers
            self._worldLayer.addToProject(project)
            self._gpsLayer.addToProject(project)
            self._speciesLayer.addToProject(project)
            self._sightingsLayer.addToProject(project)
            self._observersLayer.addToProject(project)
            self._followersLayer.addToProject(project)
            self._environmentLayer.addToProject(project)

            # configure project
            crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
            project.setCrs(crs)

            extent = QgsReferencedRectangle(
                self._worldLayer.layer.extent(), crs
            )
            project.viewSettings().setDefaultViewExtent(extent)

            project.setBackgroundColor(QColor(166, 206, 227))

            # save project
            self.db.writeProject(project)

        # read project
        if load:
            QgsProject.instance().read(self.db.projectUri)
            QgsSettings().setValue("qgis/enableMacros", "SessionOnly")

    def addEnvironmentFeature(self) -> QgsVectorLayer:
        layer = self.environmentLayer
        self._addFeature(layer)
        return layer

    def addSightingsFeature(self) -> QgsVectorLayer:
        layer = self.sightingsLayer
        self._addFeature(layer)
        return layer

    def addFollowersFeature(self, dt: str) -> None:
        layer = self.followersLayer
        self._addFeature(layer, dt)

    def needsSaving(self) -> None:
        for layer in [
            self.environmentLayer,
            self.sightingsLayer,
            self.followersLayer,
        ]:
            if not layer:
                continue

            if not layer.editBuffer():
                continue

            if len(layer.editBuffer().allAddedOrEditedFeatures()) != 0:
                return True

        return False

    def saveAll(self) -> None:
        for layer in [
            self.environmentLayer,
            self.sightingsLayer,
            self.followersLayer,
        ]:
            layer.commitChanges()
            layer.startEditing()

    def onStopSoundRecordingForEvent(
        self,
        recordType: RecordType,
        soundFile: str,
        soundStart: str,
        soundEnd: str,
    ) -> None:
        if recordType == RecordType.ENVIRONMENT:
            table = self.environmentLayer
        elif recordType == RecordType.SIGHTINGS:
            table = self.sightingsLayer
        else:
            table = self.followersLayer

        lastFeature = self.db.lastFeature(table)
        if not lastFeature:
            return

        idLastAddedFeature = lastFeature.id()

        field_idx = table.fields().indexOf("soundFile")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundFile)
        field_idx = table.fields().indexOf("soundStart")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundStart)
        field_idx = table.fields().indexOf("soundEnd")
        table.changeAttributeValue(idLastAddedFeature, field_idx, soundEnd)

        self.saveAll()

    def addGps(
        self, longitude: float, latitude: float, hour: int, minu: int, sec: int
    ):
        self._gpsLayer.add(longitude, latitude, hour, minu, sec)

    def _addFeature(self, layer: QgsVectorLayer, dt: str = "") -> None:
        feat = QgsVectorLayerUtils.createFeature(layer)

        if not dt:
            dt = utils.now()
        feat["dateTime"] = dt
        feat["copy"] = 0

        lastFeat = SammoDataBase.lastFeature(layer)
        if lastFeat:
            for name in lastFeat.fields().names():
                if name == "fid" or name == "dateTime":
                    continue
                feat[name] = lastFeat[name]

        if not layer.isEditable():
            layer.startEditing()
        layer.addFeature(feat)

        self.saveAll()

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
    def merge(sessionADir, sessionBDir, sessionOutputDir):
        # open input session
        sessionA = SammoSession()
        sessionA.init(sessionADir, load=False)

        sessionB = SammoSession()
        sessionB.init(sessionBDir, load=False)

        # copy wav files to output session
        for session in [sessionA, sessionB]:
            for wav in session.wavFiles:
                copy(wav, sessionOutputDir)

        # create output session
        sessionOutput = SammoSession()
        sessionOutput.init(sessionOutputDir, load=False)

        # only not already copied features are merged in dynamic layers
        request = QgsFeatureRequest(QgsExpression('"copy" = 0'))

        # copy features from sightingsLayer
        dynamicLayers = ["environmentLayer", "sightingsLayer", "gpsLayer", "followersLayer"]
        for layer in dynamicLayers:
            out = getattr(sessionOutput, layer)
            out.startEditing()

            newFid = 0
            lastFeature = SammoDataBase.lastFeature(out)
            if lastFeature:
                newFid = lastFeature["fid"] + 1

            for vl in [getattr(sessionA, layer), getattr(sessionB, layer)]:
                for feature in vl.getFeatures(request):
                    feature["fid"] = newFid
                    feature["copy"] = 1
                    out.addFeature(feature)

                    newFid += 1

            out.commitChanges()
