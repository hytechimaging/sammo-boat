# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QColor

from qgis.core import QgsVectorLayer

from ..database import (
    SammoDataBase,
    GPS_TABLE,
)

from .layer import SammoLayer


class SammoGpsLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, GPS_TABLE, "GPS")

    def _init(self, layer: QgsVectorLayer):
        symbol = layer.renderer().symbol()
        symbol.setColor(QColor(219, 30, 42))
        symbol.setSize(2)

        layer.setAutoRefreshInterval(1000)
        layer.setAutoRefreshEnabled(True)
