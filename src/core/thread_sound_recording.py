# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
import sounddevice as sd
from scipy.io.wavfile import write


class WorkerForSoundRecording(WorkerForOtherThread):
    def __init__(self, soundFilePath: str):
        super().__init__()
        self._soundFilePath = soundFilePath
        self.isStopRecordingClicked = False

    def _toDoInsideLoop(self):
        pass

    def onRecordIsFinished(self):
        write(self._soundFilePath, self.fs, self.myRecording)  # Save as WAV file

    def _onStart(self):
        self.fs = 44100  # Sample rate
        seconds = 60  # Duration of recording
        self.myRecording = sd.rec(int(seconds * self.fs), samplerate=self.fs, channels=2)

    def stop(self):
        sd.stop()
        self.onRecordIsFinished()
        super().stop()


class ThreadForSoundRecording(OtherThread):
    def start(self, soundFilePath: str):
        worker = WorkerForSoundRecording(soundFilePath)
        super().start(worker)
