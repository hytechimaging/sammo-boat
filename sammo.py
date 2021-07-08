# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession
from .src.gui.onOffEffort import SammoActionOnOffEffort
from .src.core.session import SammoSession


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.toolBar = self.iface.addToolBar("Sammo ToolBar")
        self.session = SammoSession()
        self.actionSession = SammoActionSession(
            self.iface.mainWindow(),
            self.toolBar,
            self.session
        )
        self.actionOnOffSession = SammoActionOnOffEffort(
            self.iface,
            self.toolBar,
            self.session
        )

    def initGui(self):
        self.actionSession.initGui()
        self.actionOnOffSession.initGui()

    def unload(self):
        self.actionSession.unload()
        self.actionOnOffSession.unload()
        del self.toolBar
