# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .src.gui.session_btn import SammoActionSession
from .src.gui.on_off_effort_btn import SammoOnOffEffortBtn
from .src.core.session import SammoSession
from .src.gui.add_observation_btn import SammoAddObservationBtn
from .src.gui.sound_recording_btn import SammoSoundRecordingBtn
from .src.core.thread_sound_recording import ThreadForSoundRecording
from .src.core.dashboard..dashboard_controller import SammoDashboardController
from .src.core.thread_gps import ThreadSimuGps
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature
from datetime import datetime
from .src.gui.simu_gps_btn import SammoSimuGpsBtn
from .src.core.logger import Logger


class Sammo:
    def __init__(self, iface):
        Logger.log("Sammo:__init__ - 0")
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()

        self._sessionBtn = self.createSessionBtn()
        self._onOffEffortBtn = self.createOnOffEffortBtn()
        self._addObservationBtn = self.createAddObservationBtn()
        (
            self._soundRecordingBtn,
            self._threadSoundRecording,
        ) = self.createSoundRecording()
        self._simuGpsBtn, self._threadSimuGps = self.createSimuGps()
        self._dashboardController = self.createDashboardController()

    def createDashboardController(self) -> SammoDashboardController:
        controller = SammoDashboardController(self.pluginFolder(), self._session, self.iface)
        return controller

    def createSoundRecording(
        self,
    ) -> [SammoSoundRecordingBtn, ThreadForSoundRecording]:
        soundRecordingBtn = SammoSoundRecordingBtn(
            self.iface.mainWindow(), self._toolBar
        )
        soundRecordingBtn.onChangeSoundRecordingStatusSignal.connect(
            self.onChangeSoundRecordingStatus
        )
        threadSoundRecording = ThreadForSoundRecording()
        return soundRecordingBtn, threadSoundRecording

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
            self._session.addNewFeatureToGpsTable
        )
        return [button, threadGps]

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))

    def createAddObservationBtn(self) -> SammoAddObservationBtn:
        button = SammoAddObservationBtn(self.iface.mainWindow(), self._toolBar)
        button.onClickObservationSignal.connect(self.onClickObservation)
        return button

    def createOnOffEffortBtn(self) -> SammoOnOffEffortBtn:
        button = SammoOnOffEffortBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeEffortStatusSignal.connect(self.onChangeEffortStatus)
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
        Logger.log("Sammo:unload - 0")
        if (
            self._threadSimuGps is not None
            and self._threadSimuGps.isProceeding
        ):
            self._threadSimuGps.stop()
        if self._threadSoundRecording.isProceeding:
            self._threadSoundRecording.stop()

        self._soundRecordingBtn.unload()
        self._sessionBtn.unload()
        self._onOffEffortBtn.unload()
        self._addObservationBtn.unload()
        if self._simuGpsBtn is not None:
            self._simuGpsBtn.unload()

        Logger.log("Sammo:unload - 1")
        self._dashboardController.unload()
        Logger.log("Sammo:unload - 2")
        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onCreateSession(workingDirectory, self._dashboardController.loadTable())
        self._onOffEffortBtn.onCreateSession()
        self._dashboardController.onCreateSession()
        if self._simuGpsBtn:
            self._simuGpsBtn.onCreateSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if isChecked:
            (
                feat,
                table,
            ) = self._session.getReadyToAddNewFeatureToEnvironmentTable()
            self._onOffEffortBtn.openFeatureForm(self.iface, table, feat)
        else:
            self._session.onStopEffort()
            self._addObservationBtn.onChangeEffortStatus(False)
            self._soundRecordingBtn.onStopEffort()
            if self._threadSoundRecording.isProceeding:
                self._threadSoundRecording.stop()
            self._dashboardController.onStopEffort()

    def onClickObservation(self):
        feat, table = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self._session.addNewFeatureToObservationTable(feat)

    def onChangeSoundRecordingStatus(self, isAskForRecording: bool):
        if isAskForRecording:
            dateTimeObj = datetime.now()
            time = (
                str(dateTimeObj.year)
                + "{:02d}".format(dateTimeObj.month)
                + "{:02d}".format(dateTimeObj.day)
                + "_"
                + "{:02d}".format(dateTimeObj.hour)
                + "{:02d}".format(dateTimeObj.minute)
                + "{:02d}".format(dateTimeObj.second)
            )
            soundFilePath = os.path.join(
                self._session.directoryPath,
                "sound_recording_{}.wav".format(time),
            )
            self._threadSoundRecording.start(soundFilePath)
        else:
            self._threadSoundRecording.stop()

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToEnvironmentTable(feat)
        self._soundRecordingBtn.onStartEffort()
        self._addObservationBtn.onChangeEffortStatus(True)
        self._dashboardController.onStartEffort()

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self._threadSimuGps.start()
        else:
            self._threadSimuGps.stop()
