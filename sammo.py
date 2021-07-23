# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .src.gui.session import SammoActionSession
from .src.gui.on_off_effort import SammoActionOnOffEffort
from .src.core.session import SammoSession
from .src.gui.add_observation_btn import SammoAddObservationBtn
from .src.gui.sound_recording_btn import SammoSoundRecordingBtn
from .src.core.thread_sound_recording import ThreadForSoundRecording
from .src.core.thread_gps import ThreadGps
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature
from datetime import datetime
from .src.gui.simu_gps_btn import SammoSimuGpsBtn


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()

        self._actionSession = self.createSessionBtn()
        self._onOffSessionBtn = self.createOnOffEffortBtn()
        self._addObservationBtn = self.createAddObservationBtn()
        self._soundRecordingBtn, self._threadSoundRecording \
            = self.createSoundRecording()
        self._simuGpsBtn, self._threadGps = self.createSimuGps()

    def createSoundRecording(self):
        soundRecordingBtn = SammoSoundRecordingBtn(
            self.iface.mainWindow(), self._toolBar
        )
        soundRecordingBtn.onChangeSoundRecordingStatusSignal.connect(
            self.onChangeSoundRecordingStatus
        )
        threadSoundRecording = ThreadForSoundRecording()
        return soundRecordingBtn, threadSoundRecording

    def createSimuGps(self) -> [SammoSimuGpsBtn, ThreadGps]:
        if os.environ.get("SAMMO_DEBUG") is None:
            return [None, None]

        button = SammoSimuGpsBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeSimuGpsStatusSignal.connect(self.onChangeSimuGpsStatus)
        testFilePath = os.path.join(
            self.pluginFolder(), "src/core/gps_coordinates_test.fic"
        )
        threadGps = ThreadGps(self._session, testFilePath)
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

    def createOnOffEffortBtn(self) -> SammoActionOnOffEffort:
        button = SammoActionOnOffEffort(self.iface.mainWindow(), self._toolBar)
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
        if self._threadGps.isProceeding:
            self._threadGps.stop()
        if self._threadSoundRecording.isProceeding:
            self._threadSoundRecording.stop()

        self._soundRecordingBtn.unload()
        self._actionSession.unload()
        self._onOffSessionBtn.unload()
        self._addObservationBtn.unload()
        if self._simuGpsBtn is not None:
            self._simuGpsBtn.unload()

        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onCreateSession(workingDirectory)
        self._onOffSessionBtn.onCreateSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if isChecked:
            (
                feat,
                table,
            ) = self._session.getReadyToAddNewFeatureToEnvironmentTable()
            self._onOffSessionBtn.openFeatureForm(self.iface, table, feat)
        else:
            self._session.onStopEffort()
            if self._simuGpsBtn is not None and self._simuGpsBtn.isChecked():
                self._threadGps.stop()
            self._addObservationBtn.onChangeEffortStatus(False)
            self._soundRecordingBtn.onStopEffort()
            if self._threadSoundRecording.isProceeding:
                self._threadSoundRecording.stop()

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
                self._session._directoryPath,
                "sound_recording_{}.wav".format(time),
            )
            self._threadSoundRecording.start(soundFilePath)
        else:
            self._threadSoundRecording.stop()

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToEnvironmentTable(feat)
        self._soundRecordingBtn.onStartEffort()
        if self._simuGpsBtn is not None and self._simuGpsBtn.isChecked():
            self._threadGps.start()
        self._addObservationBtn.onChangeEffortStatus(True)

    def onChangeSimuGpsStatus(self, isOn: bool):
        if not self._onOffSessionBtn.isChecked():
            return

        if self._simuGpsBtn.isChecked():
            self._threadGps.start()
        else:
            self._threadGps.stop()
