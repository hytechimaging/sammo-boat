# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
import sounddevice as sd
import soundfile as sf
import queue
from .logger import Logger
from qgis.PyQt.QtCore import pyqtSignal
from datetime import datetime, timedelta


class WorkerForSoundRecording(WorkerForOtherThread):
    onAutomaticStopTimerEndedSignal = pyqtSignal()

    def __init__(self, soundFilePath: str):
        super().__init__()
        self._soundFilePath = soundFilePath
        self._frameRate = 44100
        self._queue = queue.Queue()
        self._startRecordingTime: datetime = None
        self._automaticStopTime: datetime = None

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
            self._startRecordingTime = datetime.now()
            with sd.InputStream(
                samplerate=self._frameRate, channels=2, callback=self.callback
            ):
                while not self._isNeedToStop:
                    self.recordingLoop(file)

    def recordingLoop(self, file):
        file.write(self._queue.get())
        if self._automaticStopTime is not None:
            if self._automaticStopTime < datetime.now():
                self.onAutomaticStopTimerEndedSignal.emit()
                self._log("Automatic timer ended")
                self._automaticStopTime = None

    def _onStart(self):
        pass

    def setAutomaticStopTimer(self, duration_s: int):
        self._automaticStopTime = datetime.now() + timedelta(seconds=duration_s)
        self._log("setAutomaticStopTimer begins")


class ThreadForSoundRecording(OtherThread):
    setAutomaticStopTimerSignal = pyqtSignal(int)

    def __init__(self, onAutomaticStopRecordingTimerEndedMethod):
        super().__init__()
        self._onAutomaticStopRecordingTimerEndedMethod = onAutomaticStopRecordingTimerEndedMethod

    def start(self, soundFilePath: str):
        Logger.log("ThreadForSoundRecording::start begins")
        worker = WorkerForSoundRecording(soundFilePath)
        Logger.log("ThreadForSoundRecording::start 1")
        worker.onAutomaticStopTimerEndedSignal.connect(self._onAutomaticStopRecordingTimerEndedMethod)
        Logger.log("ThreadForSoundRecording::start 2")
        self.setAutomaticStopTimerSignal.connect(worker.setAutomaticStopTimer)
        Logger.log("ThreadForSoundRecording::start 3")
        super()._start(worker)
        Logger.log("ThreadForSoundRecording::start 4")
