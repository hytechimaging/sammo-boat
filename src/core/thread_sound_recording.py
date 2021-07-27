# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
import sounddevice as sd
import soundfile as sf
import queue


class WorkerForSoundRecording(WorkerForOtherThread):
    def __init__(self, soundFilePath: str):
        super().__init__()
        self._soundFilePath = soundFilePath
        self._frameRate = 44100
        self._queue = queue.Queue()

    def callback(self, inData, frames, time, status):
        self._queue.put(inData.copy())

    def _toDoInsideLoop(self):
        # Make sure the file is opened before recording anything:
        with sf.SoundFile(
            self._soundFilePath,
            mode="x",
            samplerate=self._frameRate,
            channels=2,
        ) as file:
            with sd.InputStream(
                samplerate=self._frameRate, channels=2, callback=self.callback
            ):
                while not self._isNeedToStop:
                    file.write(self._queue.get())

    def _onStart(self):
        pass


class ThreadForSoundRecording(OtherThread):
    def start(self, soundFilePath: str):
        worker = WorkerForSoundRecording(soundFilePath)
        super()._start(worker)
