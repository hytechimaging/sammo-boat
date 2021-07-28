# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .thread_sound_recording import ThreadForSoundRecording
from qgis.PyQt.QtCore import pyqtSignal, QObject
from datetime import datetime


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForObservationSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._workingDirectory: str = None
        self._threadSoundRecording = self.createSoundRecording()
        self._currentSoundFileName: str = None

    def unload(self):
        if self._threadSoundRecording.isProceeding:
            self._threadSoundRecording.stop()

    def createSoundRecording(self) -> ThreadForSoundRecording:
        threadSoundRecording = ThreadForSoundRecording(self.onAutomaticStopRecordingTimerEnded)
        return threadSoundRecording

    def onChangeObservationStatus(self, observationStatus: bool):
        if observationStatus:
            # on start observation
            self.changeSoundRecordingStatus(True)
        else:
            # on end observation
            self._threadSoundRecording.setAutomaticStopTimerSignal.emit(15)

    def onCreateSession(self, workingDirectory: str):
        self._workingDirectory = workingDirectory

    def changeSoundRecordingStatus(self, isAskForRecording: bool):
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

    def onAutomaticStopRecordingTimerEnded(self):
        self.onStopSoundRecordingForObservationSignal.emit(self._currentSoundFileName)
        self.changeSoundRecordingStatus(False)

