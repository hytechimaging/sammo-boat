# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature, QgsProject

from .src.core.session import SammoSession
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.core.thread_gps_extractor import ThreadGpsExtractor
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

        self.loading = False
        self.session = SammoSession(iface.mapCanvas())

        self.sessionAction = self.createSessionAction()
        self.effortAction = self.createEffortAction()
        self.environmentAction = self.createEnvironmentAction()
        self.followerAction = self.createFollowerAction()
        self.observationAction = self.createObservationAction()
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps()

        self.soundRecordingController = self.createSoundRecordingController()
        self.threadGpsExtractor = self.createGpsExtractor()
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

    def createGpsExtractor(self) -> ThreadGpsExtractor:
        threadGps = ThreadGpsExtractor(self.session)
        threadGps.addNewFeatureToGpsTableSignal.connect(self.session.addGps)
        threadGps.start()
        return threadGps

    def createFollowerAction(self):
        button = SammoFollowerAction(self.mainWindow, self.toolbar)
        button.onClickAddFollowerSignal.connect(self.onClickAddFollower)
        button.onAddFeatureToFollowerTableSignal.connect(
            self.onAddFeatureToFollowerTableSignal
        )
        return button

    def createObservationAction(self) -> SammoObservationAction:
        button = SammoObservationAction(self.mainWindow, self.toolbar)
        button.onClickObservationSignal.connect(self.onClickObservation)
        return button

    def createEffortAction(self) -> SammoEffortAction:
        button = SammoEffortAction(self.mainWindow, self.toolbar)
        button.onChangeEffortStatusSignal.connect(self.onChangeEffortStatus)
        return button

    def createEnvironmentAction(self) -> SammoEnvironmentAction:
        button = SammoEnvironmentAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onEnvironmentTriggered)
        button.add.connect(self.onEnvironmentAdd)
        return button

    def createSessionAction(self) -> SammoSessionAction:
        button = SammoSessionAction(self.mainWindow, self.toolbar)
        button.create.connect(self.onCreateSession)
        return button

    def initGui(self):
        pass

    def unload(self):
        self.threadGpsExtractor.stop()
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

    def onCreateSession(self, sessionDirectory: str) -> None:
        # init session
        self.loading = True
        self.session.init(sessionDirectory)
        self.loading = False

        self.setEnabled(True)

        self.soundRecordingController.onNewSession(sessionDirectory)

        # init simu
        if self.simuGpsAction:
            self.simuGpsAction.onNewSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if not isChecked:
            self.onStartNewTransect("E")
            self.statusDock.isEffortOn = False
        else:
            if not self.onStartNewTransect("B"):
                # the user pressed the CANCEL button of the form
                self.soundRecordingController.hardStopOfRecording()
                self.effortAction.button.setChecked(False)
                self.statusDock.isEffortOn = False
                return

        self.environmentAction.onChangeEffortStatus(isChecked)

    def onEnvironmentTriggered(self):
        if not self.onStartNewTransect("A"):
            # the user pressed the CANCEL button of the form
            self.soundRecordingController.hardStopOfRecording()

    def onStartNewTransect(self, status: str) -> bool:
        self.soundRecordingController.onStartEnvironment()
        (
            feat,
            table,
        ) = self.session.getReadyToAddNewFeatureToEnvironmentTable(status)

        return self.environmentAction.openFeatureForm(self.iface, table, feat)

    def onClickObservation(self):
        self.soundRecordingController.onStartObservation()
        feat, table = self.session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self.session.addObservation(feat)
            self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onClickAddFollower(self):
        feat, table = self.session.getReadyToAddNewFeatureToFollowerTable()
        self.followerAction.openFeatureForm(self.iface, table, feat)

    def onEnvironmentAdd(self, feat: QgsFeature) -> None:
        self.session.onStopTransect()  # stop the previous transect
        self.session.addEnvironment(feat)
        self.statusDock.isEffortOn = True
        self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onAddFeatureToFollowerTableSignal(self, feat: QgsFeature):
        self.session.addFollower(feat)

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self.threadSimuGps.start()
        else:
            self.threadSimuGps.stop()

    def onSoundRecordingStatusChanged(self, isOn: bool):
        self.statusDock.isSoundRecordingOn = isOn

    def addNewFeatureToGpsTableSignal(
        self, longitude: float, latitude: float, formattedDateTime: str
    ):
        self.session.addGps(longitude, latitude, formattedDateTime)
        self.statusDock.updateGpsLocation(longitude, latitude)

    def onProjectLoaded(self) -> None:
        if self.loading:
            return

        self.setEnabled(False)
        sessionDir = SammoSession.sessionDirectory(QgsProject.instance())

        if not sessionDir:
            return

        self.onCreateSession(sessionDir)

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
