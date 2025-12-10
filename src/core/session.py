# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Union

from qgis.utils import iface
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import (
    NULL,
    QgsProject,
    QgsGeometry,
    QgsMapLayer,
    QgsSettings,
    QgsApplication,
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
    SIGHTINGS_TABLE,
)
from .layers import (
    SammoGpsLayer,
    SammoBoatLayer,
    SammoWorldLayer,
    SammoSurveyLayer,
    SammoSpeciesLayer,
    SammoTransectLayer,
    SammoPlateformLayer,
    SammoFollowersLayer,
    SammoObserversLayer,
    SammoSightingsLayer,
    SammoSurveyTypeLayer,
    SammoEnvironmentLayer,
    SammoBehaviourSpeciesLayer,
)
from .sound_recording_controller import RecordType


class SammoSession(QObject):
    updateObs: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = SammoDataBase()

        self._gpsLayer: SammoGpsLayer = None
        self._worldLayer: SammoWorldLayer = None
        self._speciesLayer: SammoSpeciesLayer = None
        self._behaviourSpeciesLayer: SammoBehaviourSpeciesLayer = None
        self._followersLayer: SammoFollowersLayer = None
        self._observersLayer: SammoObserversLayer = None
        self._sightingsLayer: SammoSightingsLayer = None
        self._environmentLayer: SammoEnvironmentLayer = None
        self._surveyLayer: SammoSurveyLayer = None
        self._surveyTypeLayer: SammoSurveyLayer = None
        self._transectLayer: SammoTransectLayer = None
        self._plateformLayer: SammoPlateformLayer = None
        self.lastGpsInfo: Dict[
            str,
            Union[QgsGeometry, Dict[str, Union[float, datetime], datetime]],
        ] = {
            "geometry": QgsGeometry(),
            "gprmc": {
                "speed": -9999.0,
                "course": -9999.0,
                "datetime": datetime(1900, 1, 1, 0, 0, 0),
            },
            "datetime": None,
        }
        self.lastCaptureTime: datetime = datetime(1900, 1, 1, 0, 0, 0)

    @property
    def audioFolder(self) -> Path:
        return Path(self.db.directory) / "audio"

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
    def behaviourSpeciesLayer(self) -> QgsVectorLayer:
        return self._behaviourSpeciesLayer.layer

    @property
    def sightingsLayer(self) -> QgsVectorLayer:
        if self._sightingsLayer:
            return self._sightingsLayer.layer
        return None

    @property
    def boatLayer(self) -> QgsVectorLayer:
        if self._boatLayer:
            return self._boatLayer.layer
        return None

    @property
    def surveyLayer(self) -> QgsVectorLayer:
        if self._surveyLayer:
            return self._surveyLayer.layer
        return None

    @property
    def surveyTypeLayer(self) -> QgsVectorLayer:
        if self._surveyLayer:
            return self._surveyTypeLayer.layer
        return None

    @property
    def plateformLayer(self) -> QgsVectorLayer:
        if self._plateformLayer:
            return self._plateformLayer.layer
        return None

    @property
    def transectLayer(self) -> QgsVectorLayer:
        if self._transectLayer:
            return self._transectLayer.layer
        return None

    @property
    def allLayers(self) -> List[QgsVectorLayer]:
        return [
            self.environmentLayer,
            self.gpsLayer,
            self.followersLayer,
            self.observersLayer,
            self.behaviourSpeciesLayer,
            self.speciesLayer,
            self.sightingsLayer,
            self.surveyLayer,
            self.surveyTypeLayer,
            self.boatLayer,
            self.plateformLayer,
            self.transectLayer,
        ]

    def init(self, directory: str, load: bool = True) -> None:
        new = self.db.init(directory)
        if not (Path(directory) / "audio").exists():
            (Path(directory) / "audio").mkdir()

        self._worldLayer = SammoWorldLayer(self.db)

        # Administrator table
        self._plateformLayer = SammoPlateformLayer(self.db)
        self._boatLayer = SammoBoatLayer(self.db, self._plateformLayer)
        self._surveyTypeLayer = SammoSurveyTypeLayer(self.db)
        self._surveyLayer = SammoSurveyLayer(
            self.db, self._boatLayer, self._surveyTypeLayer
        )
        self._transectLayer = SammoTransectLayer(self.db)
        self._observersLayer = SammoObserversLayer(self.db)
        self._behaviourSpeciesLayer = SammoBehaviourSpeciesLayer(self.db)
        self._speciesLayer = SammoSpeciesLayer(self.db)

        self._gpsLayer = SammoGpsLayer(self.db)
        self._sightingsLayer = SammoSightingsLayer(
            self.db, self._behaviourSpeciesLayer
        )
        self._followersLayer = SammoFollowersLayer(
            self.db, self._observersLayer, self._speciesLayer
        )
        self._environmentLayer = SammoEnvironmentLayer(
            self.db,
            self._observersLayer,
            self._plateformLayer,
            self._transectLayer,
        )

        # create database if necessary
        if new:
            project = QgsProject()

            # add layers
            self._worldLayer.addToProject(project)
            self._plateformLayer.addToProject(project)
            self._boatLayer.addToProject(project)
            self._plateformLayer._link_boat(self._boatLayer)
            self._surveyTypeLayer.addToProject(project)
            self._surveyLayer.addToProject(project)
            self._transectLayer.addToProject(project)
            self._gpsLayer.addToProject(project)
            self._behaviourSpeciesLayer.addToProject(project)
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
            for layer in [
                self._gpsLayer,
                self._boatLayer,
                self._worldLayer,
                self._behaviourSpeciesLayer,
                self._speciesLayer,
                self._followersLayer,
                self._observersLayer,
                self._sightingsLayer,
                self._environmentLayer,
                self._surveyLayer,
                self._surveyTypeLayer,
                self._transectLayer,
                self._plateformLayer,
            ]:
                layer._init(layer.layer)
                layer.layer.startEditing()  # featureCount update
                layer.layer.commitChanges()
            self._observersLayer.layer.featureAdded.connect(self._updateObs)
            self._observersLayer.layer.featureDeleted.connect(self._updateObs)
            self._observersLayer.layer.afterCommitChanges.connect(
                self._updateObs
            )
            self._plateformLayer._link_boat(self._boatLayer)
            self.environmentLayer.actions().clearActions()
            self._environmentLayer.addSoundAction(self.environmentLayer)
            self._environmentLayer.addDuplicateAction(self.environmentLayer)
            self.sightingsLayer.actions().clearActions()
            self._sightingsLayer.addSoundAction(self.sightingsLayer)
            self._sightingsLayer.addDuplicateAction(self.sightingsLayer)
            self.followersLayer.actions().clearActions()
            self._followersLayer.addSoundAction(self.followersLayer)
            self._sightingsLayer.addDuplicateAction(self.followersLayer)
            QgsSettings().setValue("qgis/enableMacros", "SessionOnly")

    def surveyValues(self, layer: QgsVectorLayer) -> tuple:
        survey = (
            next(self.surveyLayer.getFeatures())
            if self.surveyLayer.featureCount() > 0
            else None
        )
        if (
            not survey
            or not survey["survey"]
            or not survey["cycle"]
            or not survey["computer"]
            or not survey["shipName"]
            or not survey["session"]
        ):
            iface.messageBar().pushWarning(
                f"{layer.name().lower()}",
                "Administration table `survey` is not fulffilled,"
                " all sighting attributes cannot be filled",
            )
            survey_value = ""
            cycle_value = ""
            computer_value = ""
            ship_value = ""
            session_value = ""
        else:
            survey_value = survey["survey"]
            cycle_value = survey["cycle"]
            computer_value = survey["computer"]
            ship_value = survey["shipName"]
            session_value = survey["session"]
        return (
            survey_value,
            cycle_value,
            computer_value,
            ship_value,
            session_value,
        )

    def addEnvironmentFeature(
        self, observers: tuple[str, str, str]
    ) -> QgsVectorLayer:
        layer = self.environmentLayer

        # Administration table values
        (
            survey_value,
            cycle_value,
            computer_value,
            ship_value,
            session_value,
        ) = self.surveyValues(layer)

        # EffortGroup management
        self.addEnvironmentEndDateTime()
        self._addFeature(
            layer,
            geom=self.lastGpsInfo["geometry"],
            speed=self.lastGpsInfo["gprmc"]["speed"],
            courseAverage=self.lastGpsInfo["gprmc"]["course"],
            survey=survey_value,
            cycle=cycle_value,
            session=session_value,
            computer=computer_value,
            shipName=ship_value,
            left=observers[0],
            center=observers[1],
            right=observers[2],
        )
        return layer

    def addEnvironmentEndDateTime(self):
        layer = self.environmentLayer
        ft = self.db.lastFeature(layer)
        if ft and not ft["endDateTime"]:
            ft["endDateTime"] = utils.now()
            layer.updateFeature(ft)

    def addSightingsFeature(self) -> QgsVectorLayer:
        layer = self.sightingsLayer
        survey_value, cycle_value, computer_value, _, _ = self.surveyValues(
            layer
        )
        self._addFeature(
            layer,
            geom=self.lastGpsInfo["geometry"],
            survey=survey_value,
            cycle=cycle_value,
            computer=computer_value,
        )
        return layer

    def addFollowersFeature(
        self, dt: str, geom: QgsGeometry, focalId: int, duplicate: bool
    ) -> None:
        layer = self.followersLayer
        survey_value, cycle_value, computer_value, _, _ = self.surveyValues(
            layer
        )
        self._addFeature(
            layer,
            dt,
            geom,
            duplicate,
            _focalId=focalId,
            survey=survey_value,
            cycle=cycle_value,
            computer=computer_value,
        )

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

            if (
                len(
                    set(
                        list(layer.editBuffer().addedFeatures().keys())
                        + list(
                            layer.editBuffer().changedAttributeValues().keys()
                        )
                        + list(layer.editBuffer().changedGeometries().keys())
                    )
                )
                != 0
            ):
                return True

        return False

    def saveAll(self) -> None:
        for layer in [
            self.environmentLayer,
            self.sightingsLayer,
            self.followersLayer,
        ]:
            if not layer:
                continue
            layer.commitChanges()
            layer.startEditing()

    def validate(self, merge=False) -> None:
        selectedMode = bool(
            self.environmentLayer.selectedFeatureCount()
            + self.sightingsLayer.selectedFeatureCount()
            + self.followersLayer.selectedFeatureCount()
        )

        def validateFeatures(selectedLayer: QgsVectorLayer) -> None:
            selectedLayer.startEditing()
            featuresIterator = (
                selectedLayer.getSelectedFeatures()
                if selectedMode
                else selectedLayer.getFeatures()
            )
            for feat in featuresIterator:
                if feat["validated"]:
                    continue
                idx = selectedLayer.fields().indexOf("validated")
                selectedLayer.changeAttributeValue(
                    feat.id(),
                    idx,
                    not merge,
                )
            selectedLayer.commitChanges()
            selectedLayer.startEditing()
            selectedLayer.deselect(
                [f.id() for f in selectedLayer.selectedFeatures()]
            )

        for layer in (
            self.environmentLayer,
            self.sightingsLayer,
            self.followersLayer,
        ):
            validateFeatures(layer)

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
        self,
        longitude: float,
        latitude: float,
        hour: int,
        minu: int,
        sec: int,
        speed: Optional[float] = -9999.0,
        course: Optional[float] = -9999.0,
    ) -> None:
        survey = ""
        cycle = ""
        computer = ""
        if self.surveyLayer.featureCount() > 0:
            ft = next(self.surveyLayer.getFeatures())
            survey = ft["survey"]
            cycle = ft["cycle"]
            computer = ft["computer"]
        self._gpsLayer.add(
            longitude,
            latitude,
            hour,
            minu,
            sec,
            speed,
            course,
            survey,
            cycle,
            computer,
        )

    def _addFeature(
        self,
        layer: QgsVectorLayer,
        dt: str = "",
        geom: QgsGeometry = QgsGeometry(),
        duplicate: bool = False,
        **kwargs,
    ) -> None:
        feat = QgsVectorLayerUtils.createFeature(layer)

        if not dt:
            dt = utils.now()
        feat["dateTime"] = dt
        if geom:
            feat.setGeometry(geom)
        else:
            iface.messageBar().pushWarning(
                f"{layer.name().lower()}",
                "No geometry available, please check gps status",
            )

        lastFeat = SammoDataBase.lastFeature(layer)
        if lastFeat:
            if layer == self.sightingsLayer:
                feat["side"] = lastFeat["side"]
            if layer == self.environmentLayer or duplicate:
                for name in lastFeat.fields().names():
                    if name in [
                        "fid",
                        "dateTime",
                        "endDateTime",
                        "speed",
                        "courseAverage",
                        "validated",
                        "plateform",
                        "plateformHeight",
                        "survey",
                        "cycle",
                        "session",
                        "shipName",
                        "computer",
                        "transect",
                        "strateType",
                        "length",
                        "comment",
                        "species",
                        "podSize",
                        "age",
                    ]:
                        continue
                    else:
                        feat[name] = lastFeat[name]

        for key, value in kwargs.items():
            if key in ["speed", "courseAverage"] and value == -9999.0:
                continue
            elif key in layer.fields().names():
                feat[key] = value

        if not layer.isEditable():
            layer.startEditing()
        layer.addFeature(feat)

        self.saveAll()

        # Bug for the first duplicate line in a follower table,
        # back attr changes without explanation in the duplicated feature...
        # this fixe it after the processEvents()
        if lastFeat and layer == self.followersLayer:
            lastFid = lastFeat.id()
            QgsApplication.processEvents()
            layer.changeAttributeValue(
                lastFid,
                layer.fields().indexOf("back"),
                lastFeat.attribute("back"),
            )
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
    def effortCheck(environmentLayer) -> bool:
        # effort status check
        errors = []
        for ft in environmentLayer.getFeatures():
            if ft["endDateTime"] == NULL:
                errors.append(
                    "Missing endDateTime for effort starting at "
                    f"{ft['dateTime'].toPyDateTime().isoformat()}"
                )

        if errors:
            errors.append("Please, resolve errors before validation")
            QMessageBox.warning(
                None, "Errors detected in effort status", "\n".join(errors)
            )
            return False
        return True

    @staticmethod
    def applyEnvAttr(
        environmentLayer: QgsVectorLayer,
        layer: QgsVectorLayer,
    ) -> None:
        # Sightings
        layer.startEditing()
        sideKeys = {"L": "left", "R": "right", "C": "center"}
        for envFeat in environmentLayer.getFeatures():
            startDateTime = (
                envFeat["dateTime"]
                .toPyDateTime()
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            endDateTime = (
                envFeat["endDateTime"]
                .toPyDateTime()
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            request = QgsFeatureRequest().setFilterExpression(
                f"dateTime > to_datetime('{startDateTime}') and "
                f"datetime < to_datetime('{endDateTime}')"
            )
            for feat in layer.getFeatures(request):
                if layer.name() == SIGHTINGS_TABLE:
                    if feat["side"] in sideKeys.keys():
                        feat["observer"] = envFeat[sideKeys[feat["side"]]]
                feat["_effortLeg"] = envFeat["_effortLeg"]
                feat["_effortGroup"] = envFeat["_effortGroup"]
                layer.updateFeature(feat)
            layer.commitChanges()
            layer.startEditing()

    def _updateObs(self, fid: int = 0):
        self.updateObs.emit()
