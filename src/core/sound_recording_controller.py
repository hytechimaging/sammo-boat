# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from .thread_sound_recording import ThreadForSoundRecording
from qgis.PyQt.QtCore import pyqtSignal, QObject
from datetime import datetime


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForEventSignal = pyqtSignal(bool, str, str, str)
    onSoundRecordingStatusChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._workingDirectory: str = None
        self._threadSoundRecording = self._createSoundRecording()
        self._currentSoundFileName: str = None
        self._startTimerOnRecordForCurrentEvent: float = None
        self._isCurrentEventAnObservation: bool = None

    def unload(self):
        if self._threadSoundRecording.isProceeding:
            self._onAutomaticStopRecordingTimerEnded()

    def onStartObservation(self):
        self._onStartEventWhichNeedSoundRecord(True)

    def onStartEnvironment(self):
        self._onStartEventWhichNeedSoundRecord(False)

    def hardStopOfRecording(self):
        self._threadSoundRecording.stop()
        self._currentSoundFileName = None
        self.onSoundRecordingStatusChanged.emit(False)

    def _onStartEventWhichNeedSoundRecord(self, isObservation: bool):
        if not self._threadSoundRecording.isProceeding:
            # on start observation when no sound recording is in progress
            self._isCurrentEventAnObservation = isObservation
            self._startRecording(isObservation)

        else:
            if self._isCurrentEventAnObservation == isObservation:
                self._startSameEventWhenRecordingIsInProgress(isObservation)
            else:
                self._stopRecording()
                self._isCurrentEventAnObservation = isObservation
                self._startRecording(isObservation)

    def _startSameEventWhenRecordingIsInProgress(self, isObservation: bool):
        # on start same event when sound recording is in progress
        self._threadSoundRecording.setAutomaticStopTimerSignal.emit(
            -1
        )  # cancel automatic stop
        soundEnd = "{:.1f}".format(self._threadSoundRecording.recordTimer_s())
        if self._startTimerOnRecordForCurrentEvent > 0:
            soundStart = "{:.1f}".format(
                self._startTimerOnRecordForCurrentEvent
            )
        else:
            soundStart = "0"
        if isObservation:
            self._finalizeObservation(
                self._currentSoundFileName, soundStart, soundEnd
            )
        else:
            self._finalizeEnvironment(
                self._currentSoundFileName, soundStart, soundEnd
            )
        self._startTimerOnRecordForCurrentEvent = (
            self._threadSoundRecording.recordTimer_s()
        )

    def onStopEventWhichNeedSoundRecord(self):
        # on end observation or environment changes
        self._threadSoundRecording.setAutomaticStopTimerSignal.emit(15)

    def onNewSession(self, workingDirectory: str):
        self._workingDirectory = workingDirectory

    def _createSoundRecording(self) -> ThreadForSoundRecording:
        threadSoundRecording = ThreadForSoundRecording(
            self._onAutomaticStopRecordingTimerEnded
        )
        return threadSoundRecording

    def _startRecording(self, isObservation: bool):
        dateTimeObj = datetime.now()
        timeTxt = dateTimeObj.strftime("%Y%m%d_%H%M%S")
        if isObservation:
            self._currentSoundFileName = (
                "observation_sound_recording_{}.wav".format(timeTxt)
            )
        else:
            self._currentSoundFileName = (
                "environment_sound_recording_{}.wav".format(timeTxt)
            )

        soundFilePath = os.path.join(
            self._workingDirectory, self._currentSoundFileName
        )
        self._startTimerOnRecordForCurrentEvent = 0
        self._threadSoundRecording.start(soundFilePath)

        self.onSoundRecordingStatusChanged.emit(True)

    def _onAutomaticStopRecordingTimerEnded(self):
        self._stopRecording()

    def _stopRecording(self):
        soundEnd = "{:.1f}".format(self._threadSoundRecording.recordTimer_s())
        if self._startTimerOnRecordForCurrentEvent > 0:
            soundStart = "{:.1f}".format(
                self._startTimerOnRecordForCurrentEvent
            )
        else:
            soundStart = "0"

        if self._isCurrentEventAnObservation:
            self._finalizeObservation(
                self._currentSoundFileName, soundStart, soundEnd
            )
        else:
            self._finalizeEnvironment(
                self._currentSoundFileName, soundStart, soundEnd
            )

        self._threadSoundRecording.stop()
        self._currentSoundFileName = None
        self.onSoundRecordingStatusChanged.emit(False)

    def _finalizeEnvironment(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentEvent = None
        self.onStopSoundRecordingForEventSignal.emit(
            False, soundFile, soundStart, soundEnd
        )

    def _finalizeObservation(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentEvent = None
        self.onStopSoundRecordingForEventSignal.emit(
            True, soundFile, soundStart, soundEnd
        )
