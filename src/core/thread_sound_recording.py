# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
import sounddevice as sd
from scipy.io.wavfile import write
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
import queue

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(indata.copy())


class WorkerForSoundRecording(WorkerForOtherThread):
    def __init__(self, soundFilePath: str):
        super().__init__()
        self._soundFilePath = soundFilePath
        self.fs = 44100

    def _toDoInsideLoop(self):
        # Make sure the file is opened before recording anything:
        with sf.SoundFile(self._soundFilePath, mode='x', samplerate=self.fs,
                      channels=2) as file:
            with sd.InputStream(samplerate=self.fs, channels=2, callback=callback):
                while not self._isNeedToStop:
                    file.write(q.get())


class ThreadForSoundRecording(OtherThread):
    def start(self, soundFilePath: str):
        worker = WorkerForSoundRecording(soundFilePath)
        super().start(worker)
