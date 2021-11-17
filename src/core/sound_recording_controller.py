# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from enum import Enum
from datetime import datetime

from qgis.PyQt.QtCore import pyqtSignal, QObject

from .thread_sound_recording import ThreadForSoundRecording


class RecordType(Enum):
    ENVIRONMENT = 0
    OBSERVATION = 1
    FOLLOWERS = 2


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForEventSignal = pyqtSignal(RecordType, str, str, str)
    onSoundRecordingStatusChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._workingDirectory: str = None
        self._threadSoundRecording = self._createSoundRecording()
        self._currentSoundFileName: str = None
        self._startTimerOnRecordForCurrentEvent: float = None
        self._isCurrentEventAnObservation: RecordType = None

    def unload(self):
        if self._threadSoundRecording.isProceeding:
            self._onAutomaticStopRecordingTimerEnded()

    def onStartObservation(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.OBSERVATION)

    def onStartEnvironment(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.ENVIRONMENT)

    def onStartFollowers(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.FOLLOWERS)

    def hardStopOfRecording(self):
        self._threadSoundRecording.stop()
        self._currentSoundFileName = None
        self.onSoundRecordingStatusChanged.emit(False)

    def _onStartEventWhichNeedSoundRecord(self, recordType: RecordType):
        if not self._threadSoundRecording.isProceeding:
            # on start observation when no sound recording is in progress
            self._isCurrentEventRecordType = recordType
            self._startRecording(recordType)

        else:
            if self._isCurrentEventRecordType == recordType:
                self._startSameEventWhenRecordingIsInProgress(recordType)
            else:
                self._stopRecording()
                self._isCurrentEventAnObservation = isObservation
                self._startRecording(isObservation)

    def _startSameEventWhenRecordingIsInProgress(self, recordType: RecordType):
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

        if recordType == RecordType.OBSERVATION:
            self._finalizeObservation(
                self._currentSoundFileName, soundStart, soundEnd
            )
        elif recordType == RecordType.ENVIRONMENT:
            self._finalizeEnvironment(
                self._currentSoundFileName, soundStart, soundEnd
            )
        elif recordType == RecordType.FOLLOWERS:
            self._finalizeFollowers(
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

    def _startRecording(self, recordType: RecordType):
        dateTimeObj = datetime.now()
        timeTxt = dateTimeObj.strftime("%Y%m%d_%H%M%S")
        if recordType == RecordType.OBSERVATION:
            self._currentSoundFileName = (
                f"observation_sound_recording_{timeTxt}.wav"
            )
        elif recordType == RecordType.ENVIRONMENT:
            self._currentSoundFileName = (
                f"environment_sound_recording_{timeTxt}.wav"
            )
        elif recordType == RecordType.FOLLOWERS:
            self._currentSoundFileName = (
                f"followers_sound_recording_{timeTxt}.wav"
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

        if self._isCurrentEventRecordType == RecordType.OBSERVATION:
            self._finalizeObservation(
                self._currentSoundFileName, soundStart, soundEnd
            )
        elif self._isCurrentEventRecordType == RecordType.ENVIRONMENT:
            self._finalizeEnvironment(
                self._currentSoundFileName, soundStart, soundEnd
            )
        elif self._isCurrentEventRecordType == RecordType.FOLLOWERS:
            self._finalizeFollowers(
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
            RecordType.ENVIRONMENT, soundFile, soundStart, soundEnd
        )

    def _finalizeObservation(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentEvent = None
        self.onStopSoundRecordingForEventSignal.emit(
            RecordType.OBSERVATION, soundFile, soundStart, soundEnd
        )

    def _finalizeFollowers(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentEvent = None
        self.onStopSoundRecordingForEventSignal.emit(
            RecordType.FOLLOWERS, soundFile, soundStart, soundEnd
        )
