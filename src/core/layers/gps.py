# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from datetime import datetime

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayerUtils,
    QgsPointXY,
)

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

    def add(
        self,
        longitude: float,
        latitude: float,
        hour: int,
        minu: int,
        sec: int,
        speed: float = -9999.0,
        course: float = -9999.0,
    ):
        layer = self.layer
        layer.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(layer))
        feature.setGeometry(
            QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude))
        )

        now = datetime.now()
        feature.setAttribute("dateTime", now.strftime("%Y-%m-%d %H:%M:%S"))

        gpsNow = datetime(now.year, now.month, now.day, hour, minu, sec)
        feature.setAttribute(
            "gpsDateTime", gpsNow.strftime("%Y-%m-%d %H:%M:%S")
        )
        if speed != -9999.0:
            feature.setAttribute("speed", speed)
        if course != -9999.0:
            feature.setAttribute("course", course)

        layer.addFeature(feature)
        layer.commitChanges()
