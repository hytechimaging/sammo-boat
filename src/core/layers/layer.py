# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path
from qgis.core import (
    QgsAction,
    QgsProject,
    QgsVectorLayer,
    QgsEditorWidgetSetup,
)

from ..database import SammoDataBase


class SammoLayer:
    def __init__(
        self,
        db: SammoDataBase,
        table: str,
        name: str,
        soundAction: bool = False,
    ):
        self.db = db
        self.table = table
        self.name = name
        self.soundAction = soundAction

    @property
    def layer(self) -> QgsVectorLayer:
        if QgsProject.instance().mapLayersByName(self.name):
            return QgsProject.instance().mapLayersByName(self.name)[0]

        return QgsVectorLayer(self.db.tableUri(self.table))

    @property
    def uri(self) -> str:
        return self.db.tableUri(self.table)

    def addToProject(self, project: QgsProject) -> None:
        layer = self.layer
        layer.setName(self.name)
        project.addMapLayer(layer)

        if self.soundAction:
            self._addSoundAction(layer)

        self._hideWidgetFid(layer)
        self._init(layer)

    def _init(self, layer: QgsVectorLayer) -> None:
        pass

    def _hideWidgetFid(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

    def _addSoundAction(self, layer: QgsVectorLayer) -> None:
        code = f"""
import queue
import soundfile as sf
import sounddevice as sd
from pathlib import Path
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt, QObject, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSlider,
    QLabel,
)

BUFFERSIZE = 20
BLOCKSIZE = 256
SAMPLERATE = 44100


def timeformat(seconds: int) -> str:
    return ":".join([str(x).zfill(2) for x in divmod(seconds, 60)])


class AudioThread(QThread):
    time = pyqtSignal(int)

    def __init__(self, filename, offset):
        super().__init__()
        self.player = AudioPlayer(filename, offset)
        self.player.time.connect(self.time)

    def run(self):
        self.player.playSound()

    def quit(self):
        self.player.stop()
        super().quit()


class AudioPlayer(QObject):
    time = pyqtSignal(int)

    def __init__(self, filename, offset):
        super().__init__()
        self.sound = filename
        self.offset = offset
        self.nbBlock = 0
        self.q = queue.Queue(maxsize=BUFFERSIZE)

    def callback(self, outdata, frames, time, status):
        if frames != BLOCKSIZE:
            raise sd.CallbackAbort
        if status.output_underflow:
            raise sd.CallbackAbort
        try:
            data = self.q.get_nowait()
        except queue.Empty:
            raise sd.CallbackAbort
        if len(data) < len(outdata):
            outdata[: len(data)] = data
            outdata[len(data):] = (0).to_bytes(1, "big") * (
                len(outdata) - len(data)
            )
            raise sd.CallbackStop
        else:
            outdata[:] = data

    def playSound(self):
        self.playing = True
        self.nbBlock = 0
        try:
            with sf.SoundFile(self.sound) as f:
                for _ in range(BUFFERSIZE):
                    data = f.read(BLOCKSIZE, dtype="float32")
                    if not len(data):
                        break
                    self.q.put_nowait(data)
                if self.offset:
                    while self.nbBlock * BLOCKSIZE < self.offset * SAMPLERATE:
                        f.read(BLOCKSIZE, dtype="float32")
                        self.nbBlock += 1
                self.stream = sd.OutputStream(
                    samplerate=SAMPLERATE,
                    blocksize=BLOCKSIZE,
                    channels=2,
                    callback=self.callback
                )
                with self.stream:
                    timeout = BUFFERSIZE * BLOCKSIZE / SAMPLERATE
                    while len(data):
                        data = f.read(BLOCKSIZE, dtype="float32")
                        self.q.put(data, timeout=timeout)
                        self.time.emit(
                            int(self.nbBlock * BLOCKSIZE / SAMPLERATE)
                        )
                        self.nbBlock += 1
        except queue.Full:
            pass
        except Exception as e:
            print(type(e).__name__ + ": " + str(e))

    def stop(self):
        if self.playing:
            self.stream.stop()
            self.playing = False


class AudioPlayerDialog(QDialog):
    def __init__(self, filename):
        super().__init__()
        self.player: AudioPlayer
        self.thread: AudioThread
        self.filename = filename
        self.setWindowTitle(Path(self.filename).name)

        self.playButton = QPushButton()
        self.playButton.setCheckable(True)
        self.playButton.clicked.connect(self.toggleSound)
        self.playing = False

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        sound, fs = sf.read(filename)
        self.slider.setMaximum(int(sound.shape[0] / fs))
        self.slider.setSingleStep(1)

        self.label = QLabel(
            timeformat(0) + " / " + timeformat(self.slider.maximum())
        )
        self.slider.valueChanged.connect(self.updateLabel)

        self.Vlayout = QVBoxLayout(self)
        self.Hlayout = QHBoxLayout()
        self.Hlayout.addWidget(self.playButton)
        self.Hlayout.addWidget(self.label)
        self.Vlayout.addLayout(self.Hlayout)
        self.Vlayout.addWidget(self.slider)

    @property
    def playing(self):
        return self._playing

    @playing.setter
    def playing(self, state: bool):
        if state:
            self.playButton.setIcon(
                QIcon(\"{
                    (
                        Path(__file__).parent.parent.parent.parent
                        / "images"
                        / "pause.png"
                    ).as_posix()
                }\")
            )
        else:
            self.playButton.setIcon(
                QIcon(\"{
                    (
                        Path(__file__).parent.parent.parent.parent
                        / "images"
                        / "play.png"
                    ).as_posix()
                }\")
            )
        self._playing = state

    def toggleSound(self):
        if self.playButton.isChecked():
            self.thread = AudioThread(
                self.filename, self.slider.sliderPosition()
            )
            self.thread.time.connect(self.updateSlider)
            self.thread.finished.connect(self.end)
            self.thread.start()
            self.playing = True
        else:
            self.thread.quit()
            self.playing = False

    def updateSlider(self, value: int):
        self.slider.setSliderPosition(value)

    def updateLabel(self, value: int):
        self.label.setText(
            timeformat(value) + " / " + timeformat(self.slider.maximum())
        )

    def end(self):
        self.thread.time.disconnect(self.updateSlider)
        self.thread.quit()
        self.playButton.setChecked(False)
        self.playing = False
        self.slider.setSliderPosition(0)


filename = Path(\"{self.db.directory}\") / "[% soundFile %]"
dlg = AudioPlayerDialog(filename)
dlg.show()
        """

        ac = QgsAction(1, "Play", code, False)
        layer.actions().addAction(ac)
