# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsVectorLayer,
    QgsDefaultValue,
    QgsConditionalStyle,
    QgsEditorWidgetSetup,
)

from ..database import (
    SammoDataBase,
    ENVIRONMENT_TABLE,
)

from .layer import SammoLayer


class SammoEnvironmentLayer(SammoLayer):
    def __init__(self, db: SammoDataBase, observersLayer: SammoLayer):
        super().__init__(db, ENVIRONMENT_TABLE, "Environment", True)
        self.observersLayer = observersLayer

    def _init(self, layer: QgsVectorLayer):
        self._init_widgets(layer)
        self._init_conditional_style(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # status
        idx = layer.fields().indexFromName("status")
        cfg = {}
        cfg["map"] = [
            {"B": "B"},
            {"A": "A"},
            {"E": "E"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'A'"))

        # platform
        idx = layer.fields().indexFromName("plateform")
        cfg = {}
        cfg["map"] = [
            {"bridge": "bridge"},
            {"upper_deck": "upper_deck"},
            {"deck": "deck"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'upper_deck'"))

        # route type
        idx = layer.fields().indexFromName("routeType")
        cfg = {}
        cfg["map"] = [
            {"prospection": "prospection"},
            {"trawling": "trawling"},
            {"other": "other"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'prospection'"))

        # sea state
        idx = layer.fields().indexFromName("seaState")
        cfg = {
            "AllowNull": False,
            "Max": 13,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("2"))

        # wind direction
        idx = layer.fields().indexFromName("windDirection")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("71"))

        # wind force
        idx = layer.fields().indexFromName("windForce")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("71"))

        # swell direction
        idx = layer.fields().indexFromName("swellDirection")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("165"))

        # swell height
        idx = layer.fields().indexFromName("swellHeight")
        cfg = {
            "AllowNull": False,
            "Max": 20,
            "Min": 0,
            "Precision": 1,
            "Step": 0.5,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0.5"))

        # glare from
        idx = layer.fields().indexFromName("glareFrom")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # glare to
        idx = layer.fields().indexFromName("glareTo")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # glare severity
        idx = layer.fields().indexFromName("glareSever")
        cfg = {}
        cfg["map"] = [
            {"none": "none"},
            {"slight": "slight"},
            {"moderate": "moderate"},
            {"strong": "strong"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'none'"))

        # cloud cover
        idx = layer.fields().indexFromName("cloudCover")
        cfg = {
            "AllowNull": False,
            "Max": 8,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("8"))

        # visibility
        idx = layer.fields().indexFromName("visibility")
        cfg = {}
        cfg["map"] = [
            {"0.5": "0.5"},
            {"1": "1"},
            {"2": "2"},
            {"5": "5"},
            {"10": "10"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0.5"))

        # subjective
        idx = layer.fields().indexFromName("subjective")
        cfg = {}
        cfg["map"] = [{"E": "E"}, {"G": "G"}, {"M": "M"}, {"P": "P"}]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'G'"))

        # n observers
        idx = layer.fields().indexFromName("nObservers")
        cfg = {
            "AllowNull": False,
            "Max": 4,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("2"))

        # camera
        idx = layer.fields().indexFromName("camera")
        cfg = {}
        cfg["map"] = [{"ON": "ON"}, {"OFF": "OFF"}]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'ON'"))

        # soundFile, soundStart, soundEnd, dateTime
        for field in ["soundFile", "soundStart", "soundEnd", "dateTime"]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field != "dateTime":
                setup = QgsEditorWidgetSetup("Hidden", {})
                layer.setEditorWidgetSetup(idx, setup)
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

        # left/right/center
        for field in ["left", "right", "center"]:
            idx = layer.fields().indexFromName(field)
            cfg = {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": '"observer"',
                "FilterExpression": "",
                "Key": "observer",
                "Layer": self.observersLayer.layer.id(),
                "LayerName": self.observersLayer.name,
                "LayerProviderName": "ogr",
                "LayerSource": self.observersLayer.uri,
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "observer",
            }
            setup = QgsEditorWidgetSetup("ValueRelation", cfg)
            layer.setEditorWidgetSetup(idx, setup)

    def _init_conditional_style(self, layer: QgsVectorLayer) -> None:
        # glareFrom
        expr = "if (\"glareSever\" = 'none', @value != 0, False)"
        style = QgsConditionalStyle(expr)
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("glareFrom", [style])

        # glareTo
        style = QgsConditionalStyle(expr)
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("glareTo", [style])
