# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QColor
from qgis.core import QgsVectorLayer

from .layer import SammoLayer
from ..database import SammoDataBase, WORLD_TABLE


class SammoWorldLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, WORLD_TABLE, "World", True)

    def _init(self, layer: QgsVectorLayer) -> None:
        symbol = layer.renderer().symbol()
        symbolLayer = symbol.symbolLayer(0)
        symbolLayer.setColor(QColor(178, 223, 138))
        symbolLayer.setStrokeColor(QColor(119,116,104,153))
        symbol.changeSymbolLayer(0, symbolLayer)