# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import platform

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsProject,
    QgsApplication,
    QgsVectorLayer,
    QgsDefaultValue,
    QgsEditorWidgetSetup,
    QgsSvgMarkerSymbolLayer,
)

from ..utils import path

from .layer import SammoLayer


class SammoWorldLayer:
    def __init__(self):
        self.layer = QgsVectorLayer(self._worldMapPath(), "World")
        symbol = self.layer.renderer().symbol()
        symbol.setColor(QColor(178, 223, 138))

    def addToProject(self, project: QgsProject) -> None:
        project.addMapLayer(self.layer)

    @staticmethod
    def _worldMapPath() -> str:
        path = QgsApplication.instance().pkgDataPath()
        if platform.system() == "Windows":
            path = os.path.join(
                path, "resources", "data", "world_map.gpkg|layername=countries"
            )
        else:
            path = os.path.join(
                path, "resources", "data", "world_map.gpkg|layername=countries"
            )
        return path
