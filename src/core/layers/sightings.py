# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsVectorLayer,
    QgsDefaultValue,
    QgsFieldConstraints,
    QgsConditionalStyle,
    QgsEditorWidgetSetup,
    QgsSvgMarkerSymbolLayer,
)

from ..utils import path

from ..database import (
    SammoDataBase,
    SIGHTINGS_TABLE,
)

from .layer import SammoLayer


class SammoSightingsLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, SIGHTINGS_TABLE, "Sightings")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_symbology(layer)
        self._init_widgets(layer)
        self._init_conditional_style(layer)

    def _init_symbology(self, layer: QgsVectorLayer) -> None:
        # symbology
        symbol = QgsSvgMarkerSymbolLayer(path("observation_symbol.svg"))
        symbol.setSize(6)
        symbol.setFillColor(QColor("#a76dad"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # side
        idx = layer.fields().indexFromName("side")
        cfg = {}
        cfg["map"] = [
            {"L": "L"},
            {"R": "R"},
            {"C": "C"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'R'"))

        # species
        idx = layer.fields().indexFromName("species")
        cfg = {"IsMultiline": False, "UseHtml": False}
        setup = QgsEditorWidgetSetup("TextEdit", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                    ),
                    'fid'
                ) != 0,
                True,
                False
            )
            """,
        )
        layer.setFieldConstraint(
            idx,
            QgsFieldConstraints.ConstraintExpression,
            QgsFieldConstraints.ConstraintStrengthSoft,
        )

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

        # podSizeMin
        idx = layer.fields().indexFromName("podSizeMin")
        cfg = {
            "AllowNull": True,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("5"))

        # podSizeMax
        idx = layer.fields().indexFromName("podSizeMax")
        cfg = {
            "AllowNull": True,
            "Max": 1000,
            "Min": 1,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("15"))

        # age
        idx = layer.fields().indexFromName("age")
        cfg = {}
        cfg["map"] = [
            {"A": "A"},
            {"I": "I"},
            {"J": "J"},
            {"M": "M"},
            {"I1": "I1"},
            {"I2": "I2"},
            {"I3": "I3"},
            {"I4": "I4"},
            {"NA": "NA"},
            {"NULL": None},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'A'"))

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
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

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
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

        # direction
        idx = layer.fields().indexFromName("direction")
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
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("100"))

        # behaviour
        idx = layer.fields().indexFromName("behaviour")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"attracting": "attracting"},
            {"moving": "moving"},
            {"foraging": "foraging"},
            {"escape": "escape"},
            {"stationary": "stationary"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'foraging'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                array_contains(
                    array('Marine Mammal','Seabird','Ship'),
                    attribute(
                        get_feature(
                            layer_property('Species','id'),
                            'species',
                            attribute('species')
                        ),
                        'taxon'
                    )
                ),
                "behaviour" is not NULL,
                True
            )
            """,
        )

        # behavGroup
        idx = layer.fields().indexFromName("behavGroup")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"feeding_agregation": "feeding_agregation"},
            {"MFSA": "MFSA"},
            {"compact_group": "compact_group"},
            {"scattered_group": "scattered_group"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'MFSA'"))

        # behavMam
        idx = layer.fields().indexFromName("behavMam")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"bow": "bow"},
            {"milling": "milling"},
            {"fast_swimming": "fast_swimming"},
            {"slow_swimming": "slow_swimming"},
            {"diving": "diving"},
            {"breaching": "breaching"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'diving'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Marine Mammal',
                "behavMam" is not NULL,
                True
            )
            """,
        )

        # behavBird
        idx = layer.fields().indexFromName("behavBird")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"attaking": "attaking"},
            {"with_prey": "with_prey"},
            {"scavenger": "scavenger"},
            {"klepto": "klepto"},
            {"diving": "diving"},
            {"follow_boat": "follow_boat"},
            {"random_flight": "random_flight"},
            {"circular_flight": "circular_flight"},
            {"direct_flight": "direct_flight"},
            {"swimming": "swimming"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(
            idx, QgsDefaultValue("'direct_flight'")
        )
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Seabird',
                "behavBird" is not NULL,
                True
            )
            """,
        )

        # behavShip
        idx = layer.fields().indexFromName("behavShip")
        cfg = {}
        cfg["map"] = [
            {"<NULL>": "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"},
            {"fishing": "fishing"},
            {"go_ahead": "go_ahead"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        layer.setDefaultValueDefinition(idx, QgsDefaultValue("'go_ahead'"))
        layer.setConstraintExpression(
            idx,
            """
            if(
                attribute(
                    get_feature(
                        layer_property('Species','id'),
                        'species',
                        attribute('species')
                        ),
                    'taxon'
                ) LIKE 'Ship',
                "behavShip" is not NULL,
                True
            )
            """,
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

    def _init_conditional_style(self, layer: QgsVectorLayer) -> None:
        # podSize
        style = QgsConditionalStyle(
            '@value > "podSizeMax" or @value < "podSizeMin"'
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
                False
            )
            """

        taxons = "'Marine Mammal', 'Seabird', 'Ship'"
        style = QgsConditionalStyle(expr.format(taxons))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behaviour", [style])

        # behavMam
        taxon = "'Marine Mammal'"
        style = QgsConditionalStyle(expr.format(taxon))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavMam", [style])

        # behavBird
        taxon = "'Seabird'"
        style = QgsConditionalStyle(expr.format(taxon))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavBird", [style])

        # behavShip
        taxon = "'Ship'"
        style = QgsConditionalStyle(expr.format(taxon))
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("behavShip", [style])
