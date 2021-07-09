# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession, ParentOfSammoActionSession
from .src.gui.onOffEffort import SammoActionOnOffEffort
from .src.core.session import SammoSession


class Sammo(ParentOfSammoActionSession):
    def __init__(self, iface):
        self.iface = iface
        self._toolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self.actionSession = SammoActionSession(self)
        self.actionOnOffSession = SammoActionOnOffEffort(
            self.iface,
            self._toolBar,
            self._session
        )

    def initGui(self):
        self.actionSession.initGui()
        self.actionOnOffSession.initGui()

    def unload(self):
        self.actionSession.unload()
        self.actionOnOffSession.unload()
        del self._toolBar

    def onCreateSession(self):
        self.actionOnOffSession.onCreateSession()

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    @property
    def toolBar(self):
        return self._toolBar

    @property
    def session(self):
        return self._session
