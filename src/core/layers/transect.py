# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer
from ..database import (
    SammoDataBase,
    TRANSECT_TABLE,
)

from .layer import SammoLayer


class SammoTransectLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, TRANSECT_TABLE, "Transect")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer):
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
