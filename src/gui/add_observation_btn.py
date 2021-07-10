# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtWidgets import QPushButton


class IParentOfAddObservationBtn:
    """
    This is the abstract class that Sammo class
    (which is the owner of the SammoActionAddObservation
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
    def onClicObservation(self):
        pass


class AddObservationBtn:
    def __init__(self, parent: IParentOfAddObservationBtn):
        self.parent = parent
        self.button = None

    def initGui(self):
        self.button = QPushButton(self.parent.mainWindow)
        self.button.setText("Observation")
        self.button.clicked.connect(self.run)
        self.button.setEnabled(False)
        self.parent.toolBar.addWidget(self.button)

    def onStartSession(self):
        self.button.setEnabled(True)

    def onStopEffort(self):
        self.button.setEnabled(False)

    def unload(self):
        del self.button

    def run(self):
        self.parent.onClicObservation()
