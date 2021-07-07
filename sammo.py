# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.actionSession = SammoActionSession(iface)

    def initGui(self):
        self.actionSession.initGui()

    def unload(self):
        self.actionSession.unload()
