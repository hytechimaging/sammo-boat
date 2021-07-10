# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession, IParentOfSammoActionSession
from .src.gui.on_off_effort import SammoActionOnOffEffort, IParentOfSammoActionOnOffEffort
from .src.gui.add_observation_btn import AddObservationBtn, IParentOfAddObservationBtn
from .src.core.session import SammoSession


class Sammo(IParentOfSammoActionSession, IParentOfSammoActionOnOffEffort, IParentOfAddObservationBtn):
    def __init__(self, iface):
        self.iface = iface
        self._toolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self._actionSession = SammoActionSession(self)
        self._onOffSessionBtn = SammoActionOnOffEffort(self)
        self._addObservationBtn = AddObservationBtn(self)

    def initGui(self):
        self._actionSession.initGui()
        self._onOffSessionBtn.initGui()
        self._addObservationBtn.initGui()

    def unload(self):
        self._actionSession.unload()
        self._onOffSessionBtn.unload()
        self._addObservationBtn.unload()
        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onCreateSession(workingDirectory)
        self._onOffSessionBtn.onCreateSession()

    def onStartEffort(self):
        [feature, table] = self._session.getReadyToAddNewFeatureToEnvironmentTable()
        if self.iface.openFeatureForm(table, feature):
            self._session.addNewFeatureToEnvironmentTable(feature)
            self._addObservationBtn.onStartSession()

    def onStopEffort(self):
        self._session.onStopEffort()
        self._addObservationBtn.onStopEffort()

    def onClicObservation(self):
        [feature, table] = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feature):
            self._session.addNewFeatureToObservationTable(feature)

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    @property
    def toolBar(self):
        return self._toolBar

    @property
    def session(self):
        return self._session
