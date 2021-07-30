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
from ..session import SammoSession
from ..logger import Logger
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
        self._thread = ThreadDashboard()

    def onCreateSession(self):
        Logger.log("DashboardController:onCreateSession - 0")
        if not QgsProject.instance().mapLayersByName("dashboard"):
            QgsLayerDefinition.loadLayerDefinition(self._pathToLayerFile, QgsProject.instance(), QgsProject.instance().layerTreeRoot())

    def onStartEffort(self):
        pass
        # self._thread.start(self.updateTimer)

    def onStopEffort(self):
        pass
        # self._thread.stop()

    def unload(self):
        pass
        # Logger.log("DashboardController:unload - 0 - with isProceeding = " + str(self._thread.isProceeding))
        # if self._thread and self._thread.isProceeding:
        #      Logger.log("DashboardController:unload - 1")
        #      self._thread.stop()
        #      Logger.log("DashboardController:unload - 2")

    def loadTable(self) -> QgsVectorLayer:
        vLayer = QgsVectorLayer(self._pathToTableFile, "dashboard", "ogr")
        return vLayer

    def updateTimer(self):
        if not self._thread:
            return

        dateTimeObj = datetime.now()
        txt = "{:02d}:{:02d}:{:02d}".format(dateTimeObj.hour, dateTimeObj.minute,dateTimeObj.second)
        self._session.changeTxtOfDashboardLabel("effortTimer_label",txt)
        layer = QgsProject.instance().mapLayersByName("dashboard")[0]
        layer.reload()
