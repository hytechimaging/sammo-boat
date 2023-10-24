# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

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

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
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
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 0,
            "Precision": 1,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

    def _link_boat(self, boatLayer: SammoLayer):
        # shipName
        idx = self.layer.fields().indexFromName("ship")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"ship"',
            "FilterExpression": "",
            "Key": "name",
            "Layer": boatLayer.layer.id(),
            "LayerName": boatLayer.name,
            "LayerProviderName": "ogr",
            "LayerSource": boatLayer.uri,
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "name",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        res = self.layer.setEditorWidgetSetup(idx, setup)
        print(f"le res : {res}")