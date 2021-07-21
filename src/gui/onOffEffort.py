# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtWidgets import QPushButton


class ParentOfSammoActionOnOffEffort:
    """
    This is the abstract class that Sammo class
    (which is the owner of the SammoActionOnOffEffort
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
    def onStartEffort(self):
        pass

    @abstractmethod
    def onStopEffort(self):
        pass


class SammoActionOnOffEffort:
    def __init__(self, parent: ParentOfSammoActionOnOffEffort):
        self.parent = parent
        self.button = None

    def initGui(self):
        self.button = QPushButton(self.parent.mainWindow)
        self.button.setText("Effort")
        self.button.clicked.connect(self.run)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        self.parent.toolBar.addWidget(self.button)

    def onCreateSession(self):
        self.button.setEnabled(True)

    def unload(self):
        del self.button

    def run(self):
        if self.button.isChecked():
            self.parent.onStartEffort()
        else:
            self.parent.onStopEffort()
