# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .src.gui.session import SammoActionSession
from .src.gui.on_off_effort import SammoActionOnOffEffort
from .src.core.session import SammoSession
from .src.gui.add_observation_btn import SammoAddObservationBtn
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()

        self._actionSession = SammoActionSession(
            iface.mainWindow(), self._toolBar
        )
        self._actionSession.createSignal.connect(self.onCreateSession)

        self._onOffSessionBtn = SammoActionOnOffEffort(
            iface.mainWindow(), self._toolBar
        )
        self._onOffSessionBtn.onChangeEffortStatusSignal.connect(
            self.onChangeEffortStatus
        )
        self._onOffSessionBtn.onAddFeatureToEnvironmentTableSignal.connect(
            self.onAddFeatureToEnvironmentTableSignal
        )

        self._addObservationBtn = SammoAddObservationBtn(
            iface.mainWindow(), self._toolBar
        )
        self._addObservationBtn.onClickObservationSignal.connect(
            self.onClickObservation
        )

    def initGui(self):
        pass

    def unload(self):
        self._actionSession.unload()
        self._onOffSessionBtn.unload()
        self._addObservationBtn.unload()
        del self._toolBar

    def onCreateSession(self, workingDirectory: str):
        self._session.onCreateSession(workingDirectory)
        self._onOffSessionBtn.onCreateSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if isChecked:
            (
                feat,
                table,
            ) = self._session.getReadyToAddNewFeatureToEnvironmentTable()
            self._onOffSessionBtn.openFeatureForm(self.iface, table, feat)
        else:
            self._session.onStopEffort()
            self._addObservationBtn.onChangeEffortStatus(False)

    def onClickObservation(self):
        feat, table = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self._session.addNewFeatureToObservationTable(feat)

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToEnvironmentTable(feat)
        self._addObservationBtn.onChangeEffortStatus(True)
