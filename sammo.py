# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .src.gui.changeEnvironment_btn import SammoChangeEnvironmentBtn
from .src.gui.session_btn import SammoActionSession
from .src.gui.on_off_effort_btn import SammoOnOffEffortBtn
from .src.core.session import SammoSession
from .src.gui.add_follower_btn import SammoAddFollowerBtn
from .src.gui.add_observation_btn import SammoAddObservationBtn
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.gui.simu_gps_btn import SammoSimuGpsBtn
from .src.core.sound_recording_controller import SammoSoundRecordingController
from .src.gui.status_dock import StatusDock
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature, QgsProject


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self._sessionBtn = self.createSessionBtn()
        self._onOffEffortBtn = self.createOnOffEffortBtn()
        self._changeEnvironmentBtn = self.createChangeEnvironmentBtn()
        self._addFollowerBtn = self.createAddFollowerBtn()
        self._addObservationBtn = self.createAddObservationBtn()
        self._simuGpsBtn, self._threadSimuGps = self.createSimuGps()
        self._soundRecordingController = self.createSoundRecordingController()
        self._statusDock = StatusDock(self.iface)
        QgsProject.instance().readProject.connect(self.projectLoaded)

    def createSoundRecordingController(self) -> SammoSoundRecordingController:
        controller = SammoSoundRecordingController()
        controller.onStopSoundRecordingForEventSignal.connect(
            self._session.onStopSoundRecordingForEvent
        )
        controller.onSoundRecordingStatusChanged.connect(
            self.onSoundRecordingStatusChanged
        )
        return controller

    def createSimuGps(self) -> [SammoSimuGpsBtn, ThreadSimuGps]:
        if not os.environ.get("SAMMO_DEBUG"):
            return [None, None]
        button = SammoSimuGpsBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeSimuGpsStatusSignal.connect(self.onChangeSimuGpsStatus)
        testFilePath = os.path.join(
            self.pluginFolder(), "src", "core", "trace_simu_gps.csv"
        )
        threadGps = ThreadSimuGps(self._session, testFilePath)
        threadGps.addNewFeatureToGpsTableSignal.connect(
            self.addNewFeatureToGpsTableSignal
        )
        return [button, threadGps]

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))

    def createAddFollowerBtn(self) -> SammoAddFollowerBtn:
        button = SammoAddFollowerBtn(self.iface.mainWindow(), self._toolBar)
        button.onClickAddFollowerSignal.connect(self.onClickAddFollower)
        button.onAddFeatureToFollowerTableSignal.connect(
            self.onAddFeatureToFollowerTableSignal
        )
        return button

    def createAddObservationBtn(self) -> SammoAddObservationBtn:
        button = SammoAddObservationBtn(self.iface.mainWindow(), self._toolBar)
        button.onClickObservationSignal.connect(self.onClickObservation)
        return button

    def createOnOffEffortBtn(self) -> SammoOnOffEffortBtn:
        button = SammoOnOffEffortBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeEffortStatusSignal.connect(self.onChangeEffortStatus)
        return button

    def createChangeEnvironmentBtn(self) -> SammoChangeEnvironmentBtn:
        button = SammoChangeEnvironmentBtn(
            self.iface.mainWindow(), self._toolBar
        )
        button.onClickChangeEnvironmentBtn.connect(
            self.onClickChangeEnvironmentBtn
        )
        button.onAddFeatureToEnvironmentTableSignal.connect(
            self.onAddFeatureToEnvironmentTableSignal
        )
        return button

    def createSessionBtn(self) -> SammoActionSession:
        button = SammoActionSession(self.iface.mainWindow(), self._toolBar)
        button.createSignal.connect(self.onCreateSession)
        return button

    def initGui(self):
        pass

    def unload(self):
        if (
            self._threadSimuGps is not None
            and self._threadSimuGps.isProceeding
        ):
            self._threadSimuGps.stop()
        self._soundRecordingController.unload()
        self._sessionBtn.unload()
        self._onOffEffortBtn.unload()
        self._changeEnvironmentBtn.unload()
        self._addObservationBtn.unload()
        if self._simuGpsBtn is not None:
            self._simuGpsBtn.unload()

        self._statusDock.unload()
        del self._statusDock
        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onNewSession(workingDirectory)
        self._onOffEffortBtn.onNewSession()
        self._addFollowerBtn.onNewSession()
        self._addObservationBtn.onNewSession()
        self._soundRecordingController.onNewSession(workingDirectory)
        if self._simuGpsBtn:
            self._simuGpsBtn.onNewSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if not isChecked:
            self._session.onStopTransect()
            self.onStartNewTransect('E')
            self._statusDock.isEffortOn = False
        else:
            if not self.onStartNewTransect('B'):
                # the user pressed the CANCEL button of the form
                self._soundRecordingController.hardStopOfRecording()
                self._onOffEffortBtn.button.setChecked(False)
                self._statusDock.isEffortOn = False
                return

        self._changeEnvironmentBtn.onChangeEffortStatus(isChecked)

    def onClickChangeEnvironmentBtn(self):
        self._session.onStopTransect()
        if not self.onStartNewTransect('A'):
            # the user pressed the CANCEL button of the form
            self._soundRecordingController.hardStopOfRecording()

    def onStartNewTransect(self, status: str) -> bool:
        self._soundRecordingController.onStartEnvironment()
        (
            feat,
            table,
        ) = self._session.getReadyToAddNewFeatureToEnvironmentTable(status)

        return self._changeEnvironmentBtn.openFeatureForm(self.iface, table, feat)

    def onClickObservation(self):
        self._soundRecordingController.onStartObservation()
        feat, table = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self._session.addNewFeatureToObservationTable(feat)
            self._soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onClickAddFollower(self):
        feat, table = self._session.getReadyToAddNewFeatureToFollowerTable()
        self._addFollowerBtn.openFeatureForm(self.iface, table, feat)

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToEnvironmentTable(feat)
        self._statusDock.isEffortOn = True
        self._soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onAddFeatureToFollowerTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToFollowerTable(feat)

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self._threadSimuGps.start()
        else:
            self._threadSimuGps.stop()

    def onSoundRecordingStatusChanged(self, isOn: bool):
        self._statusDock.isSoundRecordingOn = isOn

    def addNewFeatureToGpsTableSignal(
        self, longitude: float, latitude: float, formattedDateTime: str
    ):
        self._session.addNewFeatureToGpsTable(
            longitude, latitude, formattedDateTime
        )
        self._statusDock.updateGpsLocation(longitude, latitude)

    def projectLoaded(self):
        try:
            workingDirectory = QgsProject.instance().readPath("./")
            self._session.onLoadProject(workingDirectory)
            self._onOffEffortBtn.onNewSession()
            self._changeEnvironmentBtn.onNewSession()
            self._addFollowerBtn.onNewSession()
            self._addObservationBtn.onNewSession()
            self._soundRecordingController.onNewSession(workingDirectory)
            if self._simuGpsBtn:
                self._simuGpsBtn.onNewSession()
        except IndexError:
            pass
