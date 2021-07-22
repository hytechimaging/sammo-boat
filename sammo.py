# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession
from .src.gui.on_off_effort import SammoActionOnOffEffort
from .src.core.session import SammoSession
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()

        self.actionSession = SammoActionSession(
                        iface.mainWindow(),
                        self._toolBar)
        self.actionSession.createSignal.connect(self.onCreateSession)

        self.actionOnOffSession = \
            SammoActionOnOffEffort(iface.mainWindow(),
                                   self._toolBar)
        self.actionOnOffSession.\
            onChangeEffortStatusSignal.connect(self.onChangeEffortStatus)
        self.actionOnOffSession.\
            onAddFeatureToEnvironmentTableSignal.\
            connect(self.onAddFeatureToEnvironmentTableSignal)

    def initGui(self):
        pass

    def unload(self):
        self.actionSession.unload()
        self.actionOnOffSession.unload()
        del self._toolBar

    def onCreateSession(self, workingDirectory : str):
        self._session.onCreateSession(workingDirectory)
        self.actionOnOffSession.onCreateSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if isChecked:
            feat, table = self._session.getReadyToAddNewFeatureToEnvironmentTable()
            self.actionOnOffSession.openFeatureForm(self.iface, table, feat)
        else:
            self._session.onStopEffort()

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToEnvironmentTable(feat)
