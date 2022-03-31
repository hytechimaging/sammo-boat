# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from enum import Enum
from pathlib import Path
from datetime import datetime

from qgis.PyQt.QtCore import pyqtSignal, QObject

from .thread_sound_recording import ThreadForSoundRecording


class RecordType(Enum):
    ENVIRONMENT = 0
    SIGHTINGS = 1
    FOLLOWERS = 2


class SammoSoundRecordingController(QObject):
    onStopSoundRecordingForEventSignal = pyqtSignal(RecordType, str, str, str)
    onSoundRecordingStatusChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._workingDirectory: str = None
        self._thread = self._createSoundRecording()
        self._soundFile: str = None
        self._startTimerOnRecordForCurrentEvent: float = None
        self._recordType: RecordType = None

    def unload(self):
        if self._thread.isProceeding:
            self._onAutomaticStopRecordingTimerEnded()

    def onStartSightings(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.SIGHTINGS)

    def onStartEnvironment(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.ENVIRONMENT)

    def onStartFollowers(self):
        self._onStartEventWhichNeedSoundRecord(RecordType.FOLLOWERS)

    def hardStopOfRecording(self):
        self._thread.stop()
        self._soundFile = None
        self.onSoundRecordingStatusChanged.emit(False)

    def interruptRecording(self):
        if self._thread.isProceeding:
            self._stopRecording()

    def _onStartEventWhichNeedSoundRecord(self, recordType: RecordType):
        if not self._thread.isProceeding:
            # on start observation when no sound recording is in progress
            self._recordType = recordType
            self._startRecording(recordType)
        else:
            if self._recordType == recordType:
                self._startSameEventWhenRecordingIsInProgress(recordType)
            else:
                self._stopRecording()
                self._recordType = recordType
                self._startRecording(recordType)

    def _startSameEventWhenRecordingIsInProgress(self, recordType: RecordType):
        # on start same event when sound recording is in progress
        self._thread.setAutomaticStopTimerSignal.emit(
            -1
        )  # cancel automatic stop
        soundEnd = "{:.1f}".format(self._thread.recordTimer_s())
        if self._startTimerOnRecordForCurrentEvent > 0:
            soundStart = "{:.1f}".format(
                self._startTimerOnRecordForCurrentEvent
            )
        else:
            soundStart = "0"

        if recordType == RecordType.SIGHTINGS:
            self._finalizeObservation(self._soundFile, soundStart, soundEnd)
        elif recordType == RecordType.ENVIRONMENT:
            self._finalizeEnvironment(self._soundFile, soundStart, soundEnd)
        elif recordType == RecordType.FOLLOWERS:
            self._finalizeFollowers(self._soundFile, soundStart, soundEnd)

        self._startTimerOnRecordForCurrentEvent = self._thread.recordTimer_s()

    def onStopEventWhichNeedSoundRecord(self, duration_sec=15):
        # on end observation or environment changes
        self._thread.setAutomaticStopTimerSignal.emit(duration_sec)

    def onNewSession(self, workingDirectory: str):
        self._workingDirectory = workingDirectory
        audioPath = Path(self._workingDirectory) / "audio"
        audioPath.mkdir(exist_ok=True)

    def _createSoundRecording(self) -> ThreadForSoundRecording:
        threadSoundRecording = ThreadForSoundRecording(
            self._onAutomaticStopRecordingTimerEnded
        )
        return threadSoundRecording

    def _startRecording(self, recordType: RecordType):
        dateTimeObj = datetime.now()
        timeTxt = dateTimeObj.strftime("%Y%m%d_%H%M%S")
        dateTxt = dateTimeObj.strftime("%Y%m%d")
        if recordType == RecordType.SIGHTINGS:
            self._soundFile = (
                f"audio/{dateTxt}/observation_sound_recording_{timeTxt}.ogg"
            )
        elif recordType == RecordType.ENVIRONMENT:
            self._soundFile = (
                f"audio/{dateTxt}/environment_sound_recording_{timeTxt}.ogg"
            )
        elif recordType == RecordType.FOLLOWERS:
            self._soundFile = (
                f"audio/{dateTxt}/followers_sound_recording_{timeTxt}.ogg"
            )

        folderPath = Path(self._workingDirectory) / "audio" / dateTxt
        folderPath.mkdir(exist_ok=True)

        soundFilePath = (
            Path(self._workingDirectory) / self._soundFile
        ).as_posix()
        self._startTimerOnRecordForCurrentEvent = 0
        self._thread.start(soundFilePath)

        self.onSoundRecordingStatusChanged.emit(True)

    def _onAutomaticStopRecordingTimerEnded(self):
        self._stopRecording()

    def _stopRecording(self):
        soundEnd = "{:.1f}".format(self._thread.recordTimer_s())
        if self._startTimerOnRecordForCurrentEvent > 0:
            soundStart = "{:.1f}".format(
                self._startTimerOnRecordForCurrentEvent
            )
        else:
            soundStart = "0"

        if self._recordType == RecordType.SIGHTINGS:
            self._finalizeObservation(self._soundFile, soundStart, soundEnd)
        elif self._recordType == RecordType.ENVIRONMENT:
            self._finalizeEnvironment(self._soundFile, soundStart, soundEnd)
        elif self._recordType == RecordType.FOLLOWERS:
            self._finalizeFollowers(self._soundFile, soundStart, soundEnd)

        self._thread.stop()
        self._soundFile = None
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
            RecordType.SIGHTINGS, soundFile, soundStart, soundEnd
        )

    def _finalizeFollowers(
        self, soundFile: str, soundStart: str, soundEnd: str
    ):
        self._startTimerOnRecordForCurrentEvent = None
        self.onStopSoundRecordingForEventSignal.emit(
            RecordType.FOLLOWERS, soundFile, soundStart, soundEnd
        )
