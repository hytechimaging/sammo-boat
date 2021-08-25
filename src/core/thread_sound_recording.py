# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
import sounddevice as sd
import soundfile as sf
import queue
from qgis.PyQt.QtCore import pyqtSignal
from datetime import datetime, timedelta


class WorkerForSoundRecording(WorkerForOtherThread):
    onAutomaticStopTimerEndedSignal = pyqtSignal()

    def __init__(self, soundFilePath: str):
        super().__init__()
        self._soundFilePath = soundFilePath
        self._frameRate = 44100
        self._queue = queue.Queue()
        self.startRecordingTime: datetime = None
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
            self.startRecordingTime = datetime.now()
            with sd.InputStream(
                samplerate=self._frameRate, channels=2, callback=self.callback
            ):
                while not self._isNeedToStop:
                    self._recordingLoop(file)

    def _recordingLoop(self, file):
        file.write(self._queue.get())
        if self._automaticStopTime:
            if self._automaticStopTime < datetime.now():
                self.onAutomaticStopTimerEndedSignal.emit()
                self._log("Automatic timer ended")
                self._automaticStopTime = None

    def _onStart(self):
        pass

    def setAutomaticStopTimer(self, duration_s: int):
        if duration_s < 0:
            self._automaticStopTime = None
        else:
            self._automaticStopTime = datetime.now() + timedelta(
                seconds=duration_s
            )


class ThreadForSoundRecording(OtherThread):
    setAutomaticStopTimerSignal = pyqtSignal(int)

    def __init__(self, onAutomaticStopRecordingTimerEndedMethod):
        super().__init__()
        self._onAutomaticStopRecordingTimerEndedMethod = (
            onAutomaticStopRecordingTimerEndedMethod
        )
        self._worker: WorkerForOtherThread = None

    def start(self, soundFilePath: str):
        self._worker = WorkerForSoundRecording(soundFilePath)
        self._worker.onAutomaticStopTimerEndedSignal.connect(
            self._onAutomaticStopRecordingTimerEndedMethod
        )
        self.setAutomaticStopTimerSignal.connect(
            self._worker.setAutomaticStopTimer
        )
        super()._start(self._worker)

    def recordTimer_s(self) -> float:
        """
        For how many seconds the sound is recorded ?
        """
        if not self.isProceeding:
            raise RuntimeError("there is no recording currently")

        return (
            datetime.now() - self._worker.startRecordingTime
        ).total_seconds()
