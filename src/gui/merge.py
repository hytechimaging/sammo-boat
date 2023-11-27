# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
from pathlib import Path
from shutil import copyfile
from typing import Optional

from qgis.PyQt import uic
from qgis.utils import iface
from qgis.PyQt.QtCore import pyqtSignal, QObject, QDir, QDate
from qgis.core import (
    QgsTask,
    QgsProject,
    QgsExpression,
    QgsApplication,
    QgsFeatureRequest,
)
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog, QFileDialog

from ..core import utils
from ..core.session import SammoSession
from ..core.database import SammoDataBase

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / "ui/merge.ui")


class SammoMergeAction(QObject):
    triggered = pyqtSignal()

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status: bool) -> None:
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar) -> None:
        self.action = QAction(parent)
        self.action.setIcon(utils.icon("merge.png"))
        self.action.setToolTip("Merge projects")
        self.action.triggered.connect(self.onClick)
        toolbar.addAction(self.action)

    def unload(self) -> None:
        del self.action

    def onClick(self) -> None:
        self.triggered.emit()


class SammoMergeDialog(QDialog, FORM_CLASS):
    mergeEnded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.dateEdit.setDate(QDate.currentDate())
        self.ok.clicked.connect(self.merge)
        self.closeButton.clicked.connect(self.close)
        self.sessionAButton.clicked.connect(self.sessionA)
        self.sessionBButton.clicked.connect(self.sessionB)
        self.sessionMergedButton.clicked.connect(self.sessionMerged)
        self.task: SammoMergeTask

    def sessionA(self) -> None:
        sessionA = QFileDialog.getExistingDirectory(
            None,
            "Session A",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionA:
            self.sessionADir.setText(sessionA)

    def sessionB(self) -> None:
        sessionB = QFileDialog.getExistingDirectory(
            None,
            "Session B",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionB:
            self.sessionBDir.setText(sessionB)

    def sessionMerged(self) -> None:
        sessionMerged = QFileDialog.getExistingDirectory(
            None,
            "Session merged",
            QDir.currentPath(),
            QFileDialog.DontUseNativeDialog,
        )

        if sessionMerged:
            self.sessionMergedDir.setText(sessionMerged)

    def merge(self) -> None:
        QgsProject.instance().clear()
        self.ok.setEnabled(False)
        self.task = SammoMergeTask(
            self.sessionADir.text(),
            self.sessionBDir.text(),
            self.sessionAGpsCheckBox.isChecked(),
            self.sessionBGpsCheckBox.isChecked(),
            self.sessionMergedDir.text(),
            self.dateEdit.date() if self.dateCheckBox.isChecked() else None,
        )
        self.task.begun.connect(self.hide)
        self.task.taskCompleted.connect(self.after_task)
        self.task.taskTerminated.connect(self.after_task)
        QgsApplication.taskManager().addTask(self.task)

    def after_task(self):
        if self.task.errorMsg:
            iface.messageBar().pushWarning("MergeTask", self.task.errorMsg)
            self.ok.setText("Failed")
        else:
            iface.messageBar().pushInfo("MergeTask", "Merge success")
            self.ok.setText("Success")
        self.show()


class SammoMergeTask(QgsTask):
    def __init__(
        self,
        sessionADir: str,
        sessionBDir: str,
        sessionAGps: bool,
        sessionBGps: bool,
        sessionMergedDir: str,
        date: Optional[QDate] = None,
    ) -> None:
        super().__init__("Sammo Merge Task")
        self.sessionADir = sessionADir
        self.sessionBDir = sessionBDir
        self.sessionAGps = sessionAGps
        self.sessionBGps = sessionBGps
        self.sessionMergedDir = sessionMergedDir
        self.date = date
        self.errorMsg = ""

    def run(self) -> bool:
        try:
            self.merge()
        except Exception as e:
            self.errorMsg = ",".join([str(i) for i in e.args])
            return False
        return True

    def merge(self) -> None:
        # open input session
        sessionA = SammoSession()
        sessionA.init(self.sessionADir, load=False)
        sessionA.effortCheck(sessionA.environmentLayer)

        sessionB = SammoSession()
        sessionB.init(self.sessionBDir, load=False)
        sessionB.effortCheck(sessionB.environmentLayer)

        # create output session
        sessionOutput = SammoSession()
        sessionOutput.init(self.sessionMergedDir, load=False)

        # copy sound files to output session
        dateInt = (
            int(self.date.toPyDate().strftime("%Y%m%d")) if self.date else 0
        )
        progress = 0
        for i, session in enumerate([sessionA, sessionB]):
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
            progress += 5
            self.setProgress(progress)

        # copy features from dynamic layers
        dynamicLayers = [
            "environmentLayer",
            "sightingsLayer",
            "followersLayer",
        ]
        dateRequest = QgsFeatureRequest()
        if self.date:
            dateString = self.date.toPyDate().strftime("%Y-%m-%d")
            dateExpression = QgsExpression(
                "to_date(datetime) >= " f"to_date('{dateString}')"
            )
            dateRequest = QgsFeatureRequest(dateExpression)
        for i, layer in enumerate(dynamicLayers):
            out = getattr(sessionOutput, layer)

            newFid = 0
            lastFeature = SammoDataBase.lastFeature(out, True)
            if lastFeature:
                newFid = lastFeature["fid"] + 1
            for vl in [getattr(sessionA, layer), getattr(sessionB, layer)]:
                for feature in vl.getFeatures(dateRequest):
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

                        out.startEditing()
                        out.addFeature(feature)
                        out.commitChanges()

            if layer == "environmentLayer":
                SammoSession.applyEnvAttr(
                    sessionOutput.environmentLayer,
                    sessionA.sightingsLayer,
                    sessionA.followersLayer,
                )
                SammoSession.applyEnvAttr(
                    sessionOutput.environmentLayer,
                    sessionB.sightingsLayer,
                    sessionB.followersLayer,
                )
            progress += 20
            self.setProgress(progress)
        # gps layer
        out = getattr(sessionOutput, "gpsLayer")
        datetimeSet = set(
            [
                ft["datetime"].toPyDateTime().replace(second=0, microsecond=0)
                for ft in out.getFeatures(dateRequest)
            ]
        )

        newFid = 0
        lastFeature = SammoDataBase.lastFeature(out, True)
        if lastFeature:
            newFid = lastFeature["fid"] + 1
        gpsVls = []
        if self.sessionAGps:
            gpsVls.append(sessionA.gpsLayer)
        if self.sessionBGps:
            gpsVls.append(sessionB.gpsLayer)
        for vl in gpsVls:
            for feature in vl.getFeatures(dateRequest):
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
        progress += 10
        self.setProgress(progress)
        # copy content of static layers only if output is empty
        staticLayers = [
            "speciesLayer",
            "behaviourSpeciesLayer",
            "surveyLayer",
            "surveyTypeLayer",
            "transectLayer",
            "plateformLayer",
            "observersLayer",
            "surveyTypeLayer",
            "behaviourSpeciesLayer",
        ]
        for layer in staticLayers:
            progress += 2
            self.setProgress(progress)
            out = getattr(sessionOutput, layer)
            if out.featureCount() < 1:
                continue

            out.startEditing()
            vl = getattr(sessionA, layer)
            for feature in vl.getFeatures(dateRequest):
                out.addFeature(feature)
            out.commitChanges()
        self.setProgress(100)
