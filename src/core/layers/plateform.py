# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer
from ..database import (
    SammoDataBase,
    PLATEFORM_TABLE,
)

from .layer import SammoLayer


class SammoPlateformLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, PLATEFORM_TABLE, "Plateform")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer):
        # shipName
        idx = layer.fields().indexFromName("ship")
        cfg = {}
        cfg["map"] = [
            {"Thalassa": "Thalassa"},
            {"Europe": "Europe"},
            {"PourquoiPas": "PourquoiPas"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # plateform
        idx = layer.fields().indexFromName("plateform")
        cfg = {}
        cfg["map"] = [
            {"bridge_inside": "bridge_inside"},
            {"bridge_outside": "bridge_outside"},
            {"upper_bridge_outside": "upper_bridge_outside"},
            {"upper_bridge_inside": "upper_bridge_inside"},
            {"deck": "deck"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # plateform
        idx = layer.fields().indexFromName("plateformHeight")
        cfg = {}
        cfg["map"] = [
            {"8": 8},
            {"14": 14},
            {"16": 16},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
