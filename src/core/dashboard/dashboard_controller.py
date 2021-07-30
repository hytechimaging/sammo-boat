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
        if not QgsProject.instance().mapLayersByName("dashboard"):
            QgsLayerDefinition.loadLayerDefinition(self._pathToLayerFile, QgsProject.instance(),
                                                   QgsProject.instance().layerTreeRoot())
        self._thread.start(self.updateTimer)

    def unload(self):
        if self._thread and self._thread.isProceeding:
            self._thread.stop()

    def loadTable(self) -> QgsVectorLayer:
        vLayer = QgsVectorLayer(self._pathToTableFile, "dashboard", "ogr")
        return vLayer

    def updateTimer(self):
        if not self._thread:
            return

        dateTimeObj = datetime.now()
        txt = "{:02d}:{:02d}:{:02d}".format(dateTimeObj.hour, dateTimeObj.minute, dateTimeObj.second)
        self._session.changeTxtOfDashboardLabel("effortTimer_label", txt)
        layer = QgsProject.instance().mapLayersByName("dashboard")[0]
        layer.reload()
