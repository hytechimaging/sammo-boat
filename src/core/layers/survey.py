# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer

from ..database import (
    SURVEY_TABLE,
    SammoDataBase,
)
from .layer import SammoLayer
from .boat import SammoBoatLayer


class SammoSurveyLayer(SammoLayer):
    def __init__(self, db: SammoDataBase, boatLayer: SammoBoatLayer):
        super().__init__(db, SURVEY_TABLE, "Survey")
        self.boatLayer = boatLayer

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
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

        # survey
        idx = layer.fields().indexFromName("survey")
        cfg = {}
        cfg["map"] = [
            {"PELGAS": "PELGAS"},
            {"PELACUS_springtime": "PELACUS_springtime"},
            {"IBTS": "IBTS"},
            {"PELACUS_automn": "PELACUS_automn"},
            {"CAMANOC": "CAMANOC"},
            {"JUVENA": "JUVENA"},
            {"CGFS": "CGFS"},
            {"EVHOE": "EVHOE"},
            {"MOOSE": "MOOSE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # shipName
        idx = layer.fields().indexFromName("shipName")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"shipName"',
            "FilterExpression": "",
            "Key": "name",
            "Layer": self.boatLayer.layer.id(),
            "LayerName": self.boatLayer.name,
            "LayerProviderName": "ogr",
            "LayerSource": self.boatLayer.uri,
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "name",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # session
        idx = layer.fields().indexFromName("session")
        cfg = {}
        cfg["map"] = [
            {"LEG1": "LEG1"},
            {"LEG2": "LEG2"},
            {"LEG3": "LEG3"},
            {"LEG4": "LEG4"},
            {"LEG5": "LEG5"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)