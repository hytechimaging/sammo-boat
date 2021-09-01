# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .thread_sound_recording import ThreadForSoundRecording
from qgis.PyQt.QtCore import pyqtSignal, QObject
from datetime import datetime


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForObservationSignal = pyqtSignal(str, str, str)
    onSoundRecordingStatusChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._workingDirectory: str = None
        self._threadSoundRecording = self.createSoundRecording()
        self._currentSoundFileName: str = None
        self._startTimerOnRecordForCurrentObservation: float = None

    def unload(self):
        if self._threadSoundRecording.isProceeding:
            self.onAutomaticStopRecordingTimerEnded()

    def createSoundRecording(self) -> ThreadForSoundRecording:
        threadSoundRecording = ThreadForSoundRecording(
            self.onAutomaticStopRecordingTimerEnded
        )
        return threadSoundRecording

    def onChangeObservationStatus(self, observationStatus: bool):
        if observationStatus and not self._threadSoundRecording.isProceeding:
            # on start observation when no sound recording is in progress
            self.changeSoundRecordingStatus(True)

        elif observationStatus and self._threadSoundRecording.isProceeding:
            # on start observation when sound recording is in progress
            self._threadSoundRecording.setAutomaticStopTimerSignal.emit(
                -1
            )  # cancel automatic stop
            soundEnd = "{:.1f}".format(
                self._threadSoundRecording.recordTimer_s()
            )
            if self._startTimerOnRecordForCurrentObservation > 0:
                soundStart = "{:.1f}".format(
                    self._startTimerOnRecordForCurrentObservation
                )
            else:
                soundStart = "0"
            self.finalizeObservation(
                self._currentSoundFileName, soundStart, soundEnd
            )
            self._startTimerOnRecordForCurrentObservation = (
                self._threadSoundRecording.recordTimer_s()
            )

        else:
            # on end observation
            self._threadSoundRecording.setAutomaticStopTimerSignal.emit(15)

    def onNewSession(self, workingDirectory: str):
        self._workingDirectory = workingDirectory

    def changeSoundRecordingStatus(self, isAskForRecording: bool):
        if isAskForRecording:
            dateTimeObj = datetime.now()
            timeTxt = dateTimeObj.strftime("%Y%m%d_%H%M%S")
            self._currentSoundFileName = "sound_recording_{}.wav".format(
                timeTxt
            )
            soundFilePath = os.path.join(
                self._workingDirectory, self._currentSoundFileName
            )
            self._startTimerOnRecordForCurrentObservation = 0
            self._threadSoundRecording.start(soundFilePath)
        else:
            self._threadSoundRecording.stop()
            self._currentSoundFileName = None

        self.onSoundRecordingStatusChanged.emit(isAskForRecording)

    def onAutomaticStopRecordingTimerEnded(self):
        soundEnd = "{:.1f}".format(self._threadSoundRecording.recordTimer_s())
        if self._startTimerOnRecordForCurrentObservation > 0:
            soundStart = "{:.1f}".format(
                self._startTimerOnRecordForCurrentObservation
            )
        else:
            soundStart = "0"
        self.finalizeObservation(
            self._currentSoundFileName, soundStart, soundEnd
        )
        self.changeSoundRecordingStatus(False)

    def finalizeObservation(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentObservation = None
        self.onStopSoundRecordingForObservationSignal.emit(
            soundFile, soundStart, soundEnd
        )
