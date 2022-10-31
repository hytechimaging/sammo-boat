# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsVectorLayer,
    QgsDefaultValue,
    QgsConditionalStyle,
    QgsEditorWidgetSetup,
    QgsSvgMarkerSymbolLayer,
)

from ..utils import path, base64File

from ..database import (
    SammoDataBase,
    FOLLOWERS_TABLE,
)

from .layer import SammoLayer, NULL


class SammoFollowersLayer(SammoLayer):
    def __init__(self, db: SammoDataBase, observersLayer, speciesLayer):
        super().__init__(db, FOLLOWERS_TABLE, "Followers", True)
        self.observersLayer = observersLayer
        self.speciesLayer = speciesLayer

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_symbology(layer)
        self._init_widgets(layer)
        self._init_conditional_style(layer)

    def _init_symbology(self, layer: QgsVectorLayer) -> None:
        # symbology
        svgBase64 = base64File(path("seabird_symbol.svg"))
        symbol = QgsSvgMarkerSymbolLayer(svgBase64)
        symbol.setSize(6)
        symbol.setFillColor(QColor("#e89d34"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # podSize
        idx = layer.fields().indexFromName("podSize")
        cfg = {
            "AllowNull": False,
            "Max": 9999,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # back
        idx = layer.fields().indexFromName("back")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
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

        # fishActivity
        idx = layer.fields().indexFromName("fishActivity")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"up_net": "up_net"},
            {"net_down": "net_down"},
            {"discard": "discard"},
            {"hauling": "hauling"},
            {"non_active": "non_active"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"A": "A"},
            {"I": "I"},
            {"J": "J"},
            {"M": "M"},
            {"I1": "I1"},
            {"I2": "I2"},
            {"I3": "I3"},
            {"I4": "I4"},
            {"NA": "NA"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # unlucky
        idx = layer.fields().indexFromName("unlucky")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"wounded": "wounded"},
            {"oiled": "oiled"},
            {"stuck_fishing_device": "stuck_fishing_device"},
            {"hook": "hook"},
            {"fish_string": "fish_string"},
            {"tag": "tag"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # soundFile, soundStart, soundEnd, dateTime
        for field in [
            "soundFile",
            "soundStart",
            "soundEnd",
            "dateTime",
            "validated",
        ]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field != "dateTime":
                setup = QgsEditorWidgetSetup("Hidden", {})
                layer.setEditorWidgetSetup(idx, setup)
            if field == "validated":
                layer.setDefaultValueDefinition(idx, QgsDefaultValue("false"))
            layer.setEditFormConfig(form_config)

        # comment
        idx = layer.fields().indexFromName("comment")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))

    def _init_conditional_style(self, layer: QgsVectorLayer) -> None:
        # species
        expr = """
            attribute(
                get_feature(
                    layer_property('Species', 'id'),
                    'species',
                    attribute('species')
                )
                , 'fid'
            ) is NULL
        """
        style = QgsConditionalStyle(expr)
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("species", [style])

        # podSize, back, fishActivity
        for fieldName in ["podSize", "back", "fishActivity"]:
            style = QgsConditionalStyle("@value is NULL")
            style.setBackgroundColor(QColor("orange"))
            layer.conditionalStyles().setFieldStyles(fieldName, [style])

        # validated
        style = QgsConditionalStyle("validated is True")
        style.setBackgroundColor(QColor(178, 223, 138))
        layer.conditionalStyles().setRowStyles([style])
