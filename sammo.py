# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession, ParentOfSammoActionSession
from .src.gui.onOffEffort import SammoActionOnOffEffort, ParentOfSammoActionOnOffEffort
from .src.core.session import SammoSession


class Sammo(ParentOfSammoActionSession, ParentOfSammoActionOnOffEffort):
    def __init__(self, iface):
        self.iface = iface
        self._toolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self.actionSession = SammoActionSession(self)
        self.actionOnOffSession = SammoActionOnOffEffort(self)

    def initGui(self):
        self.actionSession.initGui()
        self.actionOnOffSession.initGui()

    def unload(self):
        self.actionSession.unload()
        self.actionOnOffSession.unload()
        del self._toolBar

    def onCreateSession(self, workingDirectory : str):
        self._session.onCreateSession(workingDirectory)
        self.actionOnOffSession.onCreateSession()

    def onStartEffort(self):
        [feat, table] = self._session.getReadyToAddNewFeatureToEnvironmentTable()
        if self.iface.openFeatureForm(table, feat):
            self._session.addNewFeatureToEnvironmentTable(feat)

    def onStopEffort(self):
        self._session.onStopEffort()

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    @property
    def toolBar(self):
        return self._toolBar

    @property
    def session(self):
        return self._session
