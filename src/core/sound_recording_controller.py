# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from ..gui.sound_recording_btn import SammoSoundRecordingBtn
from .thread_sound_recording import ThreadForSoundRecording
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QToolBar
from datetime import datetime


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForObservationSignal = pyqtSignal(str)

    def __init__(self, parent: QObject, toolBar: QToolBar):
        super().__init__(parent)
        self._workingDirectory: str = None
        self.parent = parent
        (
            self._soundRecordingBtn,
            self._threadSoundRecording,
        ) = self.createSoundRecording(parent, toolBar)
        self._currentSoundFileName: str = None

    def unload(self):
        if self._threadSoundRecording.isProceeding:
            self._threadSoundRecording.stop()
        self._soundRecordingBtn.unload()

    def createSoundRecording(
        self, parent: QObject, toolBar: QToolBar
    ) -> [SammoSoundRecordingBtn, ThreadForSoundRecording]:
        soundRecordingBtn = SammoSoundRecordingBtn(parent, toolBar)
        soundRecordingBtn.onChangeSoundRecordingStatusSignal.connect(
            self.onChangeSoundRecordingStatus
        )
        threadSoundRecording = ThreadForSoundRecording()
        return soundRecordingBtn, threadSoundRecording

    def onChangeEffortStatus(self, effortStatus: bool):
        if effortStatus:
            # on start effort
            self._soundRecordingBtn.onStartEffort()
        else :
            # on stop effort
            self._soundRecordingBtn.onStopEffort()
            if self._threadSoundRecording.isProceeding:
                self._threadSoundRecording.stop()

    def onChangeObservationStatus(self, observationStatus: bool):
        if observationStatus:
            # on start observation
            if self._soundRecordingBtn.button.isChecked():
                return # a recording is already on
            else:
                # start sound recording
                self.automaticChangeOfSoundRecordingStatus(True)
        else:
            # on end observation
            self.onStopSoundRecordingForObservationSignal.emit(self._currentSoundFileName)
            self.automaticChangeOfSoundRecordingStatus(False)

    def automaticChangeOfSoundRecordingStatus(self, recordingStatus: bool):
        self._soundRecordingBtn.button.setChecked(recordingStatus)
        self._soundRecordingBtn.onClick()

    def onCreateSession(self, workingDirectory: str):
        self._workingDirectory = workingDirectory

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
            self._currentSoundFileName = "sound_recording_{}.wav".format(time)
            soundFilePath = os.path.join(
                self._workingDirectory,
                self._currentSoundFileName
            )
            self._threadSoundRecording.start(soundFilePath)
        else:
            self._threadSoundRecording.stop()
            self._currentSoundFileName = None

