# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtWidgets import QPushButton


class IParentOfSoundRecordingBtn:
    """
    This is the abstract class that Sammo class
    (which is the owner of the SammoActionSoundRecording
    instance) needs to inherit from
    """

    @property
    @abstractmethod
    def mainWindow(self):
        pass

    @property
    @abstractmethod
    def toolBar(self):
        pass

    @abstractmethod
    def onStartSoundRecording(self):
        pass

    @abstractmethod
    def onStopSoundRecording(self):
        pass


class SoundRecordingBtn:
    def __init__(self, parent: IParentOfSoundRecordingBtn):
        self.parent = parent
        self.button = None

    def initGui(self):
        self.button = QPushButton(self.parent.mainWindow)
        self.button.setText("Sound recording")
        self.button.clicked.connect(self.run)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        self.parent.toolBar.addWidget(self.button)

    def onStartEffort(self):
        self.button.setEnabled(True)

    def onStopEffort(self):
        self.button.setEnabled(False)

    def unload(self):
        del self.button

    def run(self):
        if self.button.isChecked():
            self.parent.onStartSoundRecording()
        else:
            self.parent.onStopSoundRecording()
