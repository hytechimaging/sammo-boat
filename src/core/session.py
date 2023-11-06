# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

import os
from pathlib import Path
from shutil import copyfile
from datetime import datetime
from typing import List, Optional, Dict, Union

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QProgressBar, QMessageBox
from qgis.PyQt.QtCore import QDate

from qgis.utils import iface
from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsMapLayer,
    QgsSettings,
    QgsExpression,
    QgsApplication,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsVectorLayerUtils,
    QgsReferencedRectangle,
    QgsCoordinateReferenceSystem,
)

from . import utils
from .status import StatusCode
from .database import (
    DB_NAME,
    SammoDataBase,
)
from .layers import (
    SammoGpsLayer,
    SammoBoatLayer,
    SammoWorldLayer,
    SammoSurveyLayer,
    SammoStrateLayer,
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


class SammoSession:
    def __init__(self):
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
        self._strateLayer: SammoStrateLayer = None
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
    def strateLayer(self) -> QgsVectorLayer:
        if self._strateLayer:
            return self._strateLayer.layer
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
            self.strateLayer,
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
        self._strateLayer = SammoStrateLayer(self.db)
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
            self.db, self._observersLayer, self._plateformLayer
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
            self._strateLayer.addToProject(project)
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
                self._transectLayer,
                self._strateLayer,
                self._plateformLayer,
            ]:
                layer._init(layer.layer)
            self._plateformLayer._link_boat(self._boatLayer)
            self.environmentLayer.actions().clearActions()
            self._environmentLayer.addSoundAction(self.environmentLayer)
            self._environmentLayer.addDuplicateAction(self.environmentLayer)
            self.sightingsLayer.actions().clearActions()
            self._sightingsLayer.addSoundAction(self.sightingsLayer)
            self._sightingsLayer.addDuplicateAction(self.sightingsLayer)
            self.followersLayer.actions().clearActions()
            self._followersLayer.addSoundAction(self.followersLayer)
            QgsSettings().setValue("qgis/enableMacros", "SessionOnly")
            self.environmentLayer.attributeValueChanged.connect(
                self.updateRouteTypeStatus
            )

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
                "Sightings",
                f"Administration table `{layer.name().lower()}` "
                "is not fulfilled,"
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

    def transectValues(self, layer: QgsVectorLayer) -> tuple:
        transect = (
            next(self.transectLayer.getFeatures())
            if self.transectLayer.featureCount() > 0
            else None
        )
        print(transect, self.transectLayer.featureCount())
        if (
            not transect
            or not transect["transect"]
            or not transect["strate"]
            or not transect["length"]
        ):
            iface.messageBar().pushWarning(
                layer.name(),
                "Administration table `transect` is not fulfilled,"
                f" all {layer.name().lower()} attributes cannot be filled",
            )
            transect_value = ""
            strate_value = ""
            length_value = 0
        else:
            transect_value = transect["transect"]
            strate_value = transect["strate"]
            length_value = transect["length"]
        return transect_value, strate_value, length_value

    def addEnvironmentFeature(self) -> QgsVectorLayer:
        layer = self.environmentLayer
        statusCode = StatusCode.display(
            StatusCode(int(bool(layer.featureCount())))
        )

        # Administration table values
        (
            survey_value,
            cycle_value,
            computer_value,
            ship_value,
            session_value,
        ) = self.surveyValues(layer)
        transect_value, strate_value, length_value = self.transectValues(layer)

        # EffortGroup management
        effortGroup = max(
            layer.maximumValue(layer.fields().indexOf("_effortGroup")), 0
        )
        if effortGroup and statusCode == StatusCode.display(StatusCode.BEGIN):
            effortGroup += 1
        effortLeg = 0
        for ft in layer.getFeatures(
            QgsFeatureRequest(QgsExpression(f"_effortGroup = {effortGroup}"))
        ):
            if ft["_effortLeg"] > effortLeg:
                effortLeg = ft["_effortLeg"]
        effortLeg += 1

        self._addFeature(
            layer,
            geom=self.lastGpsInfo["geometry"],
            status=statusCode,
            _effortGroup=effortGroup or 1,
            _effortLeg=effortLeg or 1,
            speed=self.lastGpsInfo["gprmc"]["speed"],
            courseAverage=self.lastGpsInfo["gprmc"]["course"],
            survey=survey_value,
            cycle=cycle_value,
            session=session_value,
            computer=computer_value,
            shipName=ship_value,
            transect=transect_value,
            strate_value=strate_value,
            length=length_value,
        )
        return layer

    def updateRouteTypeStatus(self, fid: int, idx: int, value: object) -> None:
        # This method is triggered by an attribute change in the environnement
        # layer. The signal attributeValueChanged send the fid of the concerned
        # feature, the index of the modified attribute and the new value of
        # this attribute.
        # If the attribute changed is routeType, we will check the previous
        # feature to check if the routeType changes between the two feature.
        # If it's so, the status of the feature that has been changed is set on
        # StatusCode.BEGIN to start a new route.

        if not self.environmentLayer or idx not in [
            self.environmentLayer.fields().indexOf("routeType"),
        ]:
            return
        elif (
            self.environmentLayer
            and idx == self.environmentLayer.fields().indexOf("routeType")
        ):
            feat = self.environmentLayer.getFeature(fid)
            request = QgsFeatureRequest().addOrderBy("dateTime", False)
            for prevFeat in self.environmentLayer.getFeatures(request):
                if prevFeat["fid"] == feat["fid"]:
                    continue
                elif prevFeat["routeType"] == feat["routeType"]:
                    self.environmentLayer.changeAttributeValue(
                        fid,
                        self.environmentLayer.fields().indexOf("_effortGroup"),
                        prevFeat["_effortGroup"],
                    )
                elif prevFeat["routeType"] != feat["routeType"]:
                    self.environmentLayer.changeAttributeValue(
                        fid,
                        self.environmentLayer.fields().indexOf("status"),
                        StatusCode.display(StatusCode.BEGIN),
                    )
                    self.environmentLayer.changeAttributeValue(
                        fid,
                        self.environmentLayer.fields().indexOf("_effortGroup"),
                        prevFeat["_effortGroup"] + 1,
                    )
                    self.environmentLayer.changeAttributeValue(
                        fid,
                        self.environmentLayer.fields().indexOf("_effortLeg"),
                        1,
                    )
                break

    def addSightingsFeature(self) -> QgsVectorLayer:
        layer = self.sightingsLayer
        survey_value, cycle_value, computer_value, _, _ = self.surveyValues(
            layer
        )
        effortGroup = 1
        effortLeg = 1
        if self.environmentLayer and self.environmentLayer.featureCount():
            ft = self.db.lastFeature(self.environmentLayer)
            effortGroup = ft["_effortGroup"]
            effortLeg = ft["_effortLeg"]
        self._addFeature(
            layer,
            geom=self.lastGpsInfo["geometry"],
            survey=survey_value,
            cycle=cycle_value,
            computer=computer_value,
            _effortGroup=effortGroup,
            _effortLeg=effortLeg,
        )
        return layer

    def addFollowersFeature(
        self, dt: str, geom: QgsGeometry, focalId: int, duplicate: bool
    ) -> None:
        layer = self.followersLayer
        survey_value, cycle_value, computer_value, _, _ = self.surveyValues(
            layer
        )
        effortGroup = 1
        effortLeg = 1
        if self.environmentLayer and self.environmentLayer.featureCount():
            ft = self.db.lastFeature(self.environmentLayer)
            effortGroup = ft["_effortGroup"]
            effortLeg = ft["_effortLeg"]
        self._addFeature(
            layer,
            dt,
            geom,
            duplicate,
            _focalId=focalId,
            survey=survey_value,
            cycle=cycle_value,
            computer=computer_value,
            _effortGroup=effortGroup,
            _effortLeg=effortLeg,
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

    def validate(self, merge=False):
        selectedMode = bool(
            self.environmentLayer.selectedFeatureCount()
            + self.sightingsLayer.selectedFeatureCount()
            + self.followersLayer.selectedFeatureCount()
        )

        self.effortCheck(self.environmentLayer)

        def validateFeatures(selectedLayer: QgsVectorLayer):
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
    ):
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

        lastFeat = SammoDataBase.lastFeature(layer)
        if lastFeat:
            if layer == self.sightingsLayer:
                feat["side"] = lastFeat["side"]
            if layer == self.environmentLayer or duplicate:
                for name in lastFeat.fields().names():
                    if name in [
                        "fid",
                        "dateTime",
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
                        "strate",
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
    def effortCheck(environmentLayer) -> None:
        # effort status check
        effortIds = environmentLayer.uniqueValues(
            environmentLayer.fields().indexOf("_effortGroup")
        )
        errors = []
        for effortId in effortIds:
            effortIt = environmentLayer.getFeatures(
                QgsFeatureRequest().setFilterExpression(
                    f"_effortGroup = {effortId}"
                )
            )
            statusCodes = {ft["datetime"]: ft["status"] for ft in effortIt}
            if (
                StatusCode.display(StatusCode.BEGIN)
                not in statusCodes.values()
            ):
                errors.append(
                    f"Missing BEGIN code for effortGroup {effortId} (before "
                    f"{min(statusCodes).toPyDateTime().isoformat()} record)"
                )

        if errors:
            errors.append("Please, resolve errors before validation")
            QMessageBox.warning(
                None, "Errors detected in effort status", "\n".join(errors)
            )
            return

    @staticmethod
    def merge(
        sessionADir: str,
        sessionBDir: str,
        sessionAGps: bool,
        sessionBGps: bool,
        sessionOutputDir: str,
        progressBar: QProgressBar,
        date: Optional[QDate] = None,
    ) -> None:
        # open input session
        sessionA = SammoSession()
        sessionA.init(sessionADir, load=False)
        sessionA.effortCheck(sessionA.environmentLayer)

        sessionB = SammoSession()
        sessionB.init(sessionBDir, load=False)
        sessionB.effortCheck(sessionB.environmentLayer)

        # create output session
        sessionOutput = SammoSession()
        sessionOutput.init(sessionOutputDir, load=False)

        # copy sound files to output session
        progressBar.setFormat("Copying sound files")
        dateInt = int(date.toPyDate().strftime("%Y%m%d")) if date else 0
        for session in [sessionA, sessionB]:
            # all this can be replace with shutil.copytree with dirs_exist_ok,
            # after python3.8
            for subdir in session.audioFolder.glob("*"):
                if not subdir.is_dir() or int(subdir.stem) < dateInt:
                    continue
                elif not (sessionOutput.audioFolder / subdir.name).exists():
                    (sessionOutput.audioFolder / subdir.name).mkdir()
                outputFolder = sessionOutput.audioFolder / subdir.name
                for file in subdir.glob("*"):
                    if (outputFolder / file.name).exists():
                        os.remove(outputFolder / file.name)
                    copyfile(file, outputFolder / file.name)

        # copy features from dynamic layers
        dynamicLayers = [
            "environmentLayer",
            "sightingsLayer",
            "gpsLayer",
            "followersLayer",
        ]
        dateRequest = QgsFeatureRequest()
        if date:
            dateString = date.toPyDate().strftime("%Y-%m-%d")
            dateExpression = QgsExpression(
                "to_date(datetime) >= " f"to_date('{dateString}')"
            )
            dateRequest = QgsFeatureRequest(dateExpression)
        for layer in dynamicLayers:
            out = getattr(sessionOutput, layer)
            nb = 0
            progressBar.setFormat(f"Copy {layer}, Total : %p%")

            newFid = 0
            lastFeature = SammoDataBase.lastFeature(out, True)
            if lastFeature:
                newFid = lastFeature["fid"] + 1
            tot = (
                getattr(sessionA, layer).featureCount()
                + getattr(sessionB, layer).featureCount()
            )
            for vl in [getattr(sessionA, layer), getattr(sessionB, layer)]:
                for feature in vl.getFeatures(dateRequest):
                    nb += 1
                    progressBar.setValue(int(100 / tot * (nb + 1)))
                    attrs = feature.attributes()[1:]

                    exist = False
                    ft_datetime = (
                        feature["datetime"]
                        .toPyDateTime()
                        .strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    request = QgsFeatureRequest(
                        QgsExpression(
                            "format_date(datetime, 'yyyy-MM-ddThh:mm:ss') = "
                            f"'{ft_datetime}'"
                        )
                    )
                    for featureOut in out.getFeatures(request):
                        if featureOut.attributes()[1:] == attrs:
                            exist = True
                            break

                    if not exist:
                        feature["fid"] = newFid
                        newFid += 1

        # gps layer
        out = getattr(sessionOutput, "gpsLayer")
        datetimeSet = set(
            [
                ft["datetime"].toPyDateTime().replace(second=0, microsecond=0)
                for ft in out.getFeatures(dateRequest)
            ]
        )
        nb = 0
        progressBar.setFormat("Copy gpsLayer, Total : %p%")

        newFid = 0
        lastFeature = SammoDataBase.lastFeature(out, True)
        if lastFeature:
            newFid = lastFeature["fid"] + 1
        tot = (
            sessionA.gpsLayer.featureCount() + sessionB.gpsLayer.featureCount()
        )
        gpsVls = []
        if sessionAGps:
            gpsVls.append(sessionA.gpsLayer)
        if sessionAGps:
            gpsVls.append(sessionB.gpsLayer)
        for vl in gpsVls:
            for feature in vl.getFeatures(dateRequest):
                nb += 1
                progressBar.setValue(int(100 / tot * (nb + 1)))
                dateTimeAttr = (
                    feature["datetime"]
                    .toPyDateTime()
                    .replace(second=0, microsecond=0)
                )
                if dateTimeAttr in datetimeSet:
                    continue
                datetimeSet.add(dateTimeAttr)
                feature["fid"] = newFid
                newFid += 1

                out.startEditing()
                out.addFeature(feature)
                out.commitChanges()

        # copy content of static layers only if output is empty
        staticLayers = [
            "speciesLayer",
            "observersLayer",
            "surveyLayer",
            "strateLayer",
            "transectLayer",
            "plateformLayer",
        ]
        for layer in staticLayers:
            out = getattr(sessionOutput, layer)
            if out.featureCount() < 1:
                continue

            out.startEditing()
            vl = getattr(sessionA, layer)
            for feature in vl.getFeatures(dateRequest):
                out.addFeature(feature)
            out.commitChanges()
