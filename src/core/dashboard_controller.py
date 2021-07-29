# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis._core import QgsVectorLayer
from qgis.core import QgsProject, QgsLayerDefinition


class SammoDashboardController:
    def __init__(self, pluginFolder: str):
        self._pathToLayerFile = os.path.join(
            pluginFolder, "src", "core", "dashboard.qlr"
        )
        self._pathToTableFile = os.path.join(
            pluginFolder, "src", "core", "dashboard.shp"
        )

    def onCreateSession(self):
        QgsLayerDefinition.loadLayerDefinition(self._pathToLayerFile, QgsProject.instance(), QgsProject.instance().layerTreeRoot())

    def LoadTable(self) -> QgsVectorLayer:
        vLayer = QgsVectorLayer(self._pathToTableFile, "dashboard", "ogr")
        if not vLayer.isValid():
            print("Layer failed to load!")
        return vLayer

