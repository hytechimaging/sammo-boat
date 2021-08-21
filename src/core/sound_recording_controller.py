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
            if self._startTimerOnRecordForCurrentObservation > 0:
                soundRecordingDatas = (
                    "{} - between the seconds {:.1f} and {:.1f} ".format(
                        self._currentSoundFileName,
                        self._startTimerOnRecordForCurrentObservation,
                        self._threadSoundRecording.recordTimer_s(),
                    )
                )
            else:
                soundRecordingDatas = (
                    "{} - from the beginning to the second {:.1f}".format(
                        self._currentSoundFileName,
                        self._threadSoundRecording.recordTimer_s(),
                    )
                )
            self.finalizeObservation(soundRecordingDatas)
            self._startTimerOnRecordForCurrentObservation = (
                self._threadSoundRecording.recordTimer_s()
            )

        else:
            # on end observation
            self._threadSoundRecording.setAutomaticStopTimerSignal.emit(15)

    def onCreateSession(self, workingDirectory: str):
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

    def onAutomaticStopRecordingTimerEnded(self):
        if self._startTimerOnRecordForCurrentObservation > 0:
            soundRecordingDatas = (
                "{} - from the second {:.1f} to the end".format(
                    self._currentSoundFileName,
                    self._startTimerOnRecordForCurrentObservation,
                )
            )
        else:
            soundRecordingDatas = self._currentSoundFileName
        self.finalizeObservation(soundRecordingDatas)
        self.changeSoundRecordingStatus(False)

    def finalizeObservation(self, soundRecordingDatas: str):
        self._startTimerOnRecordForCurrentObservation = None
        self.onStopSoundRecordingForObservationSignal.emit(soundRecordingDatas)
