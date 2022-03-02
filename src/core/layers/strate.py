# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer
from ..database import (
    SammoDataBase,
    STRATE_TABLE,
)

from .layer import SammoLayer


class SammoStrateLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, STRATE_TABLE, "Strate")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer):
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

        # region
        idx = layer.fields().indexFromName("region")
        cfg = {}
        cfg["map"] = [
            {"NEA": "NEA"},
            {"NSP": "NSP"},
            {"EA": "EA"},
            {"WC": "WC"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
