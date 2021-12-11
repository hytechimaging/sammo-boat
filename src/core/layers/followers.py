# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsVectorLayer,
    QgsDefaultValue,
    QgsEditorWidgetSetup,
    QgsSvgMarkerSymbolLayer,
)

from ..utils import path

from ..database import (
    SammoDataBase,
    FOLLOWERS_TABLE,
)

from .layer import SammoLayer


class SammoFollowersLayer(SammoLayer):
    def __init__(self, db: SammoDataBase, observersLayer, speciesLayer):
        super().__init__(db, FOLLOWERS_TABLE, "Followers")
        self.observersLayer = observersLayer
        self.speciesLayer = speciesLayer

    def _init(self, layer: QgsVectorLayer):
        self._init_symbology(layer)
        self._init_widgets(layer)

    def _init_symbology(self, layer: QgsVectorLayer) -> None:
        # symbology
        symbol = QgsSvgMarkerSymbolLayer(path("seabird_symbol.svg"))
        symbol.setSize(6)
        symbol.setFillColor(QColor("#e89d34"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

        # nFollower
        idx = layer.fields().indexFromName("nFollower")
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
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("0"))

        # podSize
        idx = layer.fields().indexFromName("podSize")
        cfg = {
            "AllowNull": False,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("10"))

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
            {"up_net": "up_net"},
            {"net_down": "net_down"},
            {"discard": "discard"},
            {"hauling": "hauling"},
            {"NON_ACTIVE": "NON_ACTIVE"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'net_down'"))

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {
            "AllowMulti": False,
            "AllowNull": False,
            "Description": '"species"',
            "FilterExpression": "",
            "Key": "species",
            "Layer": self.speciesLayer.layer.id(),
            "LayerName": self.speciesLayer.name,
            "LayerProviderName": "ogr",
            "LayerSource": self.speciesLayer.uri,
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "species",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
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
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'A'"))

        # unlucky
        idx = layer.fields().indexFromName("unlucky")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"wounded": "wounded"},
            {"oiled": "oiled"},
            {"stuck_fishing_device": "stuck_fishing_device"},
            {"hook": "hook"},
            {"fish_string": "fish_string"},
            {"tag": "tag"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(
            idx, QgsDefaultValue("'{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}'")
        )

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
        cfg = {"IsMultiline": True, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("''"))
