# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from qgis.core import (
    QgsProject,
    QgsLayerDefinition,
    QgsVectorLayer,
)
from .thread_dashboard import ThreadDashboard
from .dashboardTableInitializer import DashboardTableInitializer
from ..session import SammoSession
from datetime import datetime


class SammoDashboardController:
    def __init__(self, pluginFolder: str, session: SammoSession, iface):
        self._pathToLayerFile = os.path.join(
            pluginFolder, "src", "core", "dashboard", "dashboard.qlr"
        )
        self._pathToTableFile = os.path.join(
            pluginFolder, "src", "core", "dashboard", "dashboard.shp"
        )
        self._session: SammoSession = session
        self._iface = iface
        self._thread = ThreadDashboard(self.updateEffortTimerLabel)
        self._timeWhenEffortBegan: datetime = None
        self._isRecordingSound = False

    def onCreateSession(self):
        if not QgsProject.instance().mapLayersByName("dashboard"):
            QgsLayerDefinition.loadLayerDefinition(self._pathToLayerFile, QgsProject.instance(),
                                                   QgsProject.instance().layerTreeRoot())

    def onChangeEffortStatus(self, effortStatus: bool):
        if effortStatus:
            self._timeWhenEffortBegan = datetime.now()
            self.showUpdateEffortTimeLabel(True)
            self._startThread()
        else:
            self.endThread()
            self.showUpdateEffortTimeLabel(False)

    def onChangeSoundRecordingStatus(self, isRecording: bool):
        if isRecording:
            self.showSoundRecordingLabel(True)
        else:
            self.showSoundRecordingLabel(False)

    def unload(self):
        self.endThread()

    def _startThread(self):
        if not self._thread.isProceeding:
            self._thread.start()

    def endThread(self):
        if self._thread and self._thread.isProceeding:
            self._thread.stop()

    def loadTable(self) -> QgsVectorLayer:
        vLayer = QgsVectorLayer(self._pathToTableFile, "dashboard", "ogr")
        return vLayer

    def showUpdateEffortTimeLabel(self, isVisible: bool):
        id = DashboardTableInitializer.effortTimer_ID
        if isVisible:
            self._session.changeOffsetsDashboardLabel(id, DashboardTableInitializer.effortTimer_offset_x)
        else:
            self._session.changeOffsetsDashboardLabel(id, DashboardTableInitializer.Invisible_offset_x)

        self.updateEffortTimerLabel()

    def showSoundRecordingLabel(self, isVisible: bool):
        id = DashboardTableInitializer.soundRecording_ID
        if isVisible:
            self._session.changeOffsetsDashboardLabel(id, DashboardTableInitializer.soundRecording_offset_x)
        else:
            self._session.changeOffsetsDashboardLabel(id, DashboardTableInitializer.Invisible_offset_x)

        self.reloadDashboard()

    def updateEffortTimerLabel(self):
        txt = ""
        if self._timeWhenEffortBegan:
            elapsed = datetime.now() - self._timeWhenEffortBegan
            hours = divmod(elapsed.seconds, 3600)[0]
            minutes = divmod(elapsed.seconds - 3600 * hours, 60)[0]
            seconds = elapsed.seconds - hours * 3600 - minutes * 60
            txt = "Effort - {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        self._session.changeTxtOfDashboardLabel(1, txt)
        self.reloadDashboard()

    @staticmethod
    def reloadDashboard():
        layer = QgsProject.instance().mapLayersByName("dashboard")[0]
        layer.reload()
