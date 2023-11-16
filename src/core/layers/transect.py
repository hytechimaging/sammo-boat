# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis.PyQt.QtGui import QColor
from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer, QgsLineSymbol
from ..database import (
    SammoDataBase,
    TRANSECT_TABLE,
)

from .layer import SammoLayer


class SammoTransectLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, TRANSECT_TABLE, "Transect")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_symbology(layer)
        self._init_widgets(layer)

    def _init_symbology(self, layer) -> None:
        symbol = QgsLineSymbol.createSimple(
            {"color": QColor("red"), "width": "1.5"}
        )
        layer.renderer().setSymbol(symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # strate
        idx = layer.fields().indexFromName("strate")
        cfg = {}
        cfg["map"] = [
            {"Neritic": "Neritic"},
            {"Oceanic": "Oceanic"},
            {"Slope": "Slope"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # subRegion
        idx = layer.fields().indexFromName("subRegion")
        cfg = {}
        cfg["map"] = [
            {"MED": "MED"},
            {"ATL": "ATL"},
            {"MAN": "MAN"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
