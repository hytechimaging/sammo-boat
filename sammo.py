# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from datetime import datetime

from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsProject, QgsVectorLayerUtils

from .src.core.gps import SammoGpsReader
from .src.core.session import SammoSession
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.core.sound_recording_controller import SammoSoundRecordingController

from .src.gui.status import StatusDock
from .src.gui.effort import SammoEffortAction
from .src.gui.session import SammoSessionAction
from .src.gui.simu_gps import SammoSimuGpsAction
from .src.gui.follower import SammoFollowerAction
from .src.gui.observation import SammoObservationAction
from .src.gui.environment import SammoEnvironmentAction


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self.toolbar.setObjectName("Sammo ToolBar")

        self.loading = False
        self.session = SammoSession()

        self.sessionAction = self.createSessionAction()
        self.effortAction = self.createEffortAction()
        self.environmentAction = self.createEnvironmentAction()
        self.followerAction = self.createFollowerAction()
        self.observationAction = self.createObservationAction()
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps()

        self.soundRecordingController = self.createSoundRecordingController()
        self.gpsReader = self.createGpsReader()
        self.statusDock = StatusDock(iface)

        iface.projectRead.connect(self.onProjectLoaded)
        iface.newProjectCreated.connect(self.onProjectLoaded)

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    def setEnabled(self, status):
        self.statusDock.setEnabled(status)
        self.effortAction.setEnabled(status)
        self.followerAction.setEnabled(status)
        self.observationAction.setEnabled(status)

    def createSoundRecordingController(self) -> SammoSoundRecordingController:
        controller = SammoSoundRecordingController()
        controller.onStopSoundRecordingForEventSignal.connect(
            self.session.onStopSoundRecordingForEvent
        )
        controller.onSoundRecordingStatusChanged.connect(
            self.onSoundRecordingStatusChanged
        )
        return controller

    def createSimuGps(self) -> [SammoSimuGpsAction, ThreadSimuGps]:
        if not os.environ.get("SAMMO_DEBUG"):
            return [None, None]
        button = SammoSimuGpsAction(self.mainWindow, self.toolbar)
        button.onChangeSimuGpsStatusSignal.connect(self.onChangeSimuGpsStatus)
        testFilePath = os.path.join(
            self.pluginFolder(), "src", "core", "trace_simu_gps.csv"
        )
        threadGps = ThreadSimuGps(self.session, testFilePath)
        threadGps.addNewFeatureToGpsTableSignal.connect(
            self.addNewFeatureToGpsTableSignal
        )
        return [button, threadGps]

    def createGpsReader(self) -> SammoGpsReader:
        gps = SammoGpsReader()
        gps.frame.connect(self.onGpsFrame)
        gps.start()
        return gps

    def createFollowerAction(self):
        button = SammoFollowerAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onFollowerAction)
        return button

    def createObservationAction(self) -> SammoObservationAction:
        button = SammoObservationAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onObservationAction)
        return button

    def createEffortAction(self) -> SammoEffortAction:
        button = SammoEffortAction(self.mainWindow, self.toolbar)
        button.updateEffort.connect(self.onEffortAction)
        return button

    def createEnvironmentAction(self) -> SammoEnvironmentAction:
        button = SammoEnvironmentAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onEnvironmentAction)
        return button

    def createSessionAction(self) -> SammoSessionAction:
        button = SammoSessionAction(self.mainWindow, self.toolbar)
        button.create.connect(self.onCreateSession)
        return button

    def initGui(self):
        pass

    def unload(self):
        self.gpsReader.stop()

        if self.threadSimuGps is not None and self.threadSimuGps.isProceeding:
            self.threadSimuGps.stop()
        self.soundRecordingController.unload()
        self.sessionAction.unload()
        self.effortAction.unload()
        self.environmentAction.unload()
        self.observationAction.unload()
        if self.simuGpsAction is not None:
            self.simuGpsAction.unload()

        self.statusDock.unload()
        del self.statusDock
        del self.toolbar

    def onGpsFrame(self, longitude, latitude, h, m, s):
        self.session.addGps(longitude, latitude, h, m, s)
        self.statusDock.updateGpsInfo(longitude, latitude)

    def onCreateSession(self, sessionDirectory: str) -> None:
        # init session
        self.loading = True
        self.session.init(sessionDirectory)
        self.loading = False

        self.gpsReader.active = True
        self.setEnabled(True)

        self.soundRecordingController.onNewSession(sessionDirectory)

        # init simu
        if self.simuGpsAction:
            self.simuGpsAction.onNewSession()

    def onEffortAction(self, onEffort: bool):
        if not onEffort:
            if self.updateEffort("E"):  # cancel
                self.statusDock.isEffortOn = False
            else:
                self.effortAction.action.setChecked(True)
        else:
            if not self.updateEffort("B"):
                # the user pressed the CANCEL button of the form
                self.effortAction.action.setChecked(False)
                self.statusDock.isEffortOn = False
            else:
                self.statusDock.isEffortOn = True

        self.environmentAction.onChangeEffortStatus(self.statusDock.isEffortOn)

    def updateEffort(self, status: str = "A") -> bool:
        self.soundRecordingController.onStartEnvironment()

        layer = self.session.environmentLayer
        feat = QgsVectorLayerUtils.createFeature(layer)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feat["status"] = status

        layer.startEditing()
        if self.iface.openFeatureForm(layer, feat):
            layer.addFeature(feat)
            layer.commitChanges()
            self.soundRecordingController.onStopEventWhichNeedSoundRecord()
            return True
        else:
            self.soundRecordingController.hardStopOfRecording()
            layer.rollBack()
            return False

    def onObservationAction(self):
        self.soundRecordingController.onStartObservation()

        layer = self.session.sightingsLayer
        feat = QgsVectorLayerUtils.createFeature(layer)
        if self.session.lastGpsGeom:
            feat.setGeometry(self.session.lastGpsGeom)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        layer.startEditing()
        if self.iface.openFeatureForm(layer, feat):
            layer.addFeature(feat)
            layer.commitChanges()
            self.soundRecordingController.onStopEventWhichNeedSoundRecord()
        else:
            self.soundRecordingController.hardStopOfRecording()
            layer.rollBack()

    def onFollowerAction(self):
        layer = self.session.followerLayer
        feat = QgsVectorLayerUtils.createFeature(layer)

        if self.session.lastGpsGeom:
            feat.setGeometry(self.session.lastGpsGeom)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        layer.startEditing()
        if self.iface.openFeatureForm(layer, feat):
            layer.addFeature(feat)
            layer.commitChanges()
        else:
            layer.rollBack()

    def onEnvironmentAction(self) -> None:
        if self.updateEffort():
            self.statusDock.isEffortOn = True
            self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self.threadSimuGps.start()
        else:
            self.threadSimuGps.stop()

    def onSoundRecordingStatusChanged(self, isOn: bool):
        self.statusDock.isSoundRecordingOn = isOn

    def onProjectLoaded(self) -> None:
        if self.loading:
            return

        self.gpsReader.active = False
        self.setEnabled(False)
        sessionDir = SammoSession.sessionDirectory(QgsProject.instance())

        if not sessionDir:
            return

        self.onCreateSession(sessionDir)

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
