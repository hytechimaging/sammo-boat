# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .src.gui.session import SammoActionSession, IParentOfSammoActionSession
from .src.gui.on_off_effort import SammoActionOnOffEffort, IParentOfSammoActionOnOffEffort
from .src.gui.sound_recording_btn import SoundRecordingBtn, IParentOfSoundRecordingBtn
from .src.gui.add_observation_btn import AddObservationBtn, IParentOfAddObservationBtn
from .src.core.session import SammoSession
from .src.core.thread_gps import ThreadGps
from .src.core.thread_sound_recording import ThreadForSoundRecording


class Sammo(IParentOfSammoActionSession,
            IParentOfSammoActionOnOffEffort,
            IParentOfAddObservationBtn,
            IParentOfSoundRecordingBtn
            ):
    def __init__(self, iface):
        self.iface = iface
        self._toolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self._actionSession = SammoActionSession(self)
        self._onOffSessionBtn = SammoActionOnOffEffort(self)
        self._addObservationBtn = AddObservationBtn(self)
        self._soundRecordingBtn = SoundRecordingBtn(self)

        self._threadGps = ThreadGps(self._session)
        self._threadSoundRecording = ThreadForSoundRecording()
        self._threadGps.addNewFeatureToGpsTableSignal.connect(self._session.addNewFeatureToGpsTable)

    def initGui(self):
        self._actionSession.initGui()
        self._onOffSessionBtn.initGui()
        self._addObservationBtn.initGui()
        self._soundRecordingBtn.initGui()

    def unload(self):
        self._actionSession.unload()
        self._onOffSessionBtn.unload()
        self._addObservationBtn.unload()
        self._soundRecordingBtn.unload()
        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onCreateSession(workingDirectory)
        self._onOffSessionBtn.onCreateSession()

    def onStartEffort(self):
        [feature, table] = self._session.getReadyToAddNewFeatureToEnvironmentTable()
        if self.iface.openFeatureForm(table, feature):
            self._session.addNewFeatureToEnvironmentTable(feature)
            self._addObservationBtn.onStartSession()
            self._soundRecordingBtn.onStartEffort()
            testFilePath = os.path.join(self._session._directoryPath, "gps_coordinates_test.fic")
            self._threadGps.start(testFilePath)

    def onStopEffort(self):
        self._session.onStopEffort()
        self._addObservationBtn.onStopEffort()
        self._threadGps.stop()
        self._soundRecordingBtn.onStopEffort()

    def onClicObservation(self):
        [feature, table] = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feature):
            self._session.addNewFeatureToObservationTable(feature)

    def onStartSoundRecording(self):
        soundFilePath = os.path.join(self._session._directoryPath, "test.wav")
        self._threadSoundRecording.start(soundFilePath)

    def onStopSoundRecording(self):
        self._threadSoundRecording.stop()

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    @property
    def toolBar(self):
        return self._toolBar

    @property
    def session(self):
        return self._session
