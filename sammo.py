from .src.gui.session import SammoActionSession


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.actionSession = SammoActionSession(iface)

    def initGui(self):
        self.actionSession.initGui()

    def unload(self):
        self.actionSession.unload()
