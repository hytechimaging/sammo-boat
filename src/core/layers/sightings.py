# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

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
    SIGHTINGS_TABLE,
)

from .layer import SammoLayer, NULL


class SammoSightingsLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, SIGHTINGS_TABLE, "Sightings", True)

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_symbology(layer)
        self._init_widgets(layer)
        self._init_conditional_style(layer)

    def _init_symbology(self, layer: QgsVectorLayer) -> None:
        # symbology
        svgBase64 = base64File(path("observation_symbol.svg"))
        symbol = QgsSvgMarkerSymbolLayer(svgBase64)
        symbol.setSize(6)
        symbol.setFillColor(QColor("#a76dad"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # side
        idx = layer.fields().indexFromName("side")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"L": "L"},
            {"R": "R"},
            {"C": "C"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # podSize
        idx = layer.fields().indexFromName("podSize")
        cfg = {
            "AllowNull": False,
            "Max": 9999,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # podSizeMin
        idx = layer.fields().indexFromName("podSizeMin")
        cfg = {
            "AllowNull": True,
            "Max": 9999,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # podSizeMax
        idx = layer.fields().indexFromName("podSizeMax")
        cfg = {
            "AllowNull": True,
            "Max": 9999,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"NULL": NULL},
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

        # distance
        idx = layer.fields().indexFromName("distance")
        cfg = {
            "AllowNull": False,
            "Max": 20000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # angle
        idx = layer.fields().indexFromName("angle")
        cfg = {
            "AllowNull": False,
            "Max": 360,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # direction
        idx = layer.fields().indexFromName("direction")
        cfg = {
            "AllowNull": True,
            "Max": 360,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # behaviour
        idx = layer.fields().indexFromName("behaviour")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"attraction": "attraction"},
            {"moving": "moving"},
            {"foraging": "foraging"},
            {"escape": "escape"},
            {"stationary": "stationary"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # behavGroup
        idx = layer.fields().indexFromName("behavGroup")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"feeding_agregation": "feeding_agregation"},
            {"MFSA": "MFSA"},
            {"compact_group": "compact_group"},
            {"scattered_group": "scattered_group"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # behavMam
        idx = layer.fields().indexFromName("behavMam")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"bow": "bow"},
            {"milling": "milling"},
            {"fast_swimming": "fast_swimming"},
            {"slow_swimming": "slow_swimming"},
            {"diving": "diving"},
            {"breaching": "breaching"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # behavBird
        idx = layer.fields().indexFromName("behavBird")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"attacked": "attacked"},
            {"with_prey": "with_prey"},
            {"klepto": "klepto"},
            {"diving": "diving"},
            {"follow_boat": "follow_boat"},
            {"random_flight": "random_flight"},
            {"circular_flight": "circular_flight"},
            {"straight_flight": "straight_flight"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # behavShip
        idx = layer.fields().indexFromName("behavShip")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": NULL},
            {"fishing": "fishing"},
            {"route": "route"},
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
            "sightNum",
            "observer",
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
        # side, distance
        expr = "@value is NULL"
        style = QgsConditionalStyle(expr)
        style.setBackgroundColor(QColor("orange"))
        for fieldName in ["side", "distance"]:
            layer.conditionalStyles().setFieldStyles(fieldName, [style])

        # podSize
        style = QgsConditionalStyle(
            '@value > "podSizeMax" or @value < "podSizeMin" or @value is NULL'
        )
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("podSize", [style])

        # podSizeMin
        style = QgsConditionalStyle(
            '@value > "podSizeMax" or @value > "podSize"'
        )
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("podSizeMin", [style])

        # podSizeMax
        style = QgsConditionalStyle(
            '@value < "podSizeMin" or @value < "podSize"'
        )
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("podSizeMax", [style])

        # angle
        style = QgsConditionalStyle(
            """
            (@value > 91 and @value < 269) or @value is NULL
        """
        )
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("angle", [style])

        # behaviour
        expr = """
            if (
                array_contains(
                    array({}),
                    attribute(
                        get_feature(
                            layer_property('Species', 'id'),
                            'species',
                            attribute('species')
                        )
                        , 'taxon'
                    )
                ),
                @value is NULL,
                {}
            )
            """
        addExpr = """
            (
                if(  "behavMam" ,1,0) +
                if(  "behavBird" ,1,0) +
                if(  "behavShip" ,1,0)
                > 1
            )
            """

        taxons = "'Marine Mammal', 'Seabird', 'Ship'"
        style = QgsConditionalStyle(expr.format(taxons, "False"))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behaviour", [style])

        # behavMam
        taxon = "'Marine Mammal'"
        style = QgsConditionalStyle(expr.format(taxon, addExpr))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavMam", [style])

        # behavBird
        taxon = "'Seabird'"
        style = QgsConditionalStyle(expr.format(taxon, addExpr))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavBird", [style])

        # behavShip
        taxon = "'Ship'"
        style = QgsConditionalStyle(expr.format(taxon, addExpr))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavShip", [style])

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

        # validated
        style = QgsConditionalStyle("validated is True")
        style.setBackgroundColor(QColor(178, 223, 138))
        layer.conditionalStyles().setRowStyles([style])
