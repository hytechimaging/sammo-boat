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

        self.session = SammoSession()

        self.sessionAction = self.createSessionAction()
        self.effortAction = self.createEffortAction()
        self.environmentAction = self.createEnvironmentAction()
        self.followerAction = self.createFollowerAction()
        self.observationAction = self.createObservationAction()
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps()

        self.soundRecordingController = self.createSoundRecordingController()
        self.threadGpsExtractor = self.createGpsExtractor()
        self.statusDock = StatusDock(self.iface)
        QgsProject.instance().readProject.connect(self.projectLoaded)

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
        button = SammoSimuGpsBtn(self.mainWindow, self.toolbar)
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
        threadGps.addNewFeatureToGpsTableSignal.connect(
            self.session.addNewFeatureToGpsTable
        )
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
        button = SammoEnvironmentAction(
            self.mainWindow, self.toolbar
        )
        button.onClickChangeEnvironmentBtn.connect(
            self.onClickChangeEnvironmentBtn
        )
        button.onAddFeatureToEnvironmentTableSignal.connect(
            self.onAddFeatureToEnvironmentTableSignal
        )
        return button

    def createSessionAction(self) -> SammoSessionAction:
        button = SammoSessionAction(self.mainWindow, self.toolbar)
        button.create.connect(self.onCreateSession)
        return button

    def initGui(self):
        pass

    def unload(self):
        self.threadGpsExtractor.stop()
        if (
            self.threadSimuGps is not None
            and self.threadSimuGps.isProceeding
        ):
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

    def onCreateSession(self, workingDirectory: str):
        self.session.onNewSession(workingDirectory)
        self.effortAction.onNewSession()
        self.followerAction.onNewSession()
        self.observationAction.onNewSession()
        self.soundRecordingController.onNewSession(workingDirectory)
        if self.simuGpsAction:
            self.simuGpsAction.onNewSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if not isChecked:
            self.onStartNewTransect("E")
            self.statusDock.isEffortOn = False
        else:
            if not self.onStartNewTransect("B"):
                # the user pressed the CANCEL button of the form
                self._soundRecordingController.hardStopOfRecording()
                self._onOffEffortBtn.button.setChecked(False)
                self.statusDock.isEffortOn = False
                return

        self.environmentAction.onChangeEffortStatus(isChecked)

    def onClickChangeEnvironmentBtn(self):
        if not self.onStartNewTransect("A"):
            # the user pressed the CANCEL button of the form
            self.soundRecordingController.hardStopOfRecording()

    def onStartNewTransect(self, status: str) -> bool:
        self._soundRecordingController.onStartEnvironment()
        (
            feat,
            table,
        ) = self.session.getReadyToAddNewFeatureToEnvironmentTable(status)

        return self._changeEnvironmentBtn.openFeatureForm(
            self.iface, table, feat
        )

    def onClickObservation(self):
        self.soundRecordingController.onStartObservation()
        feat, table = self.session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self.session.addNewFeatureToObservationTable(feat)
            self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onClickAddFollower(self):
        feat, table = self.session.getReadyToAddNewFeatureToFollowerTable()
        self.followerAction.openFeatureForm(self.iface, table, feat)

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self.session.onStopTransect()  # stop the previous transect
        self.session.addNewFeatureToEnvironmentTable(feat)
        self.statusDock.isEffortOn = True
        self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onAddFeatureToFollowerTableSignal(self, feat: QgsFeature):
        self.session.addNewFeatureToFollowerTable(feat)

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
        self.session.addNewFeatureToGpsTable(
            longitude, latitude, formattedDateTime
        )
        self.statusDock.updateGpsLocation(longitude, latitude)

    def projectLoaded(self):
        try:
            workingDirectory = QgsProject.instance().readPath("./")
            self.session.onLoadProject(workingDirectory)
            self.effortAction.onNewSession()
            self.environmentAction.onNewSession()
            self.followerAction.onNewSession()
            self.observationAction.onNewSession()
            self.soundRecordingController.onNewSession(workingDirectory)
            if self.simuGpsAction:
                self.simuGpsAction.onNewSession()
        except IndexError:
            pass

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
