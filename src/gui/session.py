# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from abc import abstractmethod
from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QAction, QFileDialog


class ParentOfSammoActionSession:
    """
    This is the abstract class that Sammo class
    (which is the owner of the SammoActionSession
    instance) needs to inherit from
    """

    @abstractmethod
    def onCreateSession(self, workingDirectory : str):
        pass

    @property
    @abstractmethod
    def mainWindow(self):
        pass

    @property
    @abstractmethod
    def toolBar(self):
        pass

    @property
    @abstractmethod
    def session(self):
        pass


class SammoActionSession:
    def __init__(self, parent: ParentOfSammoActionSession):
        self.parent = parent
        self.action = None

    def initGui(self):
        self.action = QAction("Session", self.parent.mainWindow)
        self.action.triggered.connect(self.run)
        self.parent.toolBar.addAction(self.action)

    def unload(self):
        del self.action

    def run(self):
        workingDirectory = QFileDialog.getExistingDirectory(
            None, "Select a working directory", QDir.currentPath()
        )
        if not workingDirectory:
            # no directory selected
            return

        self.parent.onCreateSession(workingDirectory)
