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
    ENVIRONMENT_TABLE,
)

from .layer import SammoLayer
from .transect import SammoTransectLayer
from .plateform import SammoPlateformLayer
from .observers import SammoObserversLayer


class SammoEnvironmentLayer(SammoLayer):
    def __init__(
        self,
        db: SammoDataBase,
        observersLayer: SammoObserversLayer,
        plateformLayer: SammoPlateformLayer,
        transectLayer: SammoTransectLayer,
    ):
        super().__init__(
            db,
            ENVIRONMENT_TABLE,
            "Environment",
            soundAction=True,
            duplicateAction=True,
        )
        self.observersLayer = observersLayer
        self.plateformLayer = plateformLayer
        self.transectLayer = transectLayer

    def _init(self, layer: QgsVectorLayer):
        self._init_symbology(layer)
        self._init_widgets(layer)
        self._init_conditional_style(layer)

    def _init_symbology(self, layer: QgsVectorLayer) -> None:
        # symbology
        svgBase64 = base64File(path("environment_symbol.svg"))
        symbol = QgsSvgMarkerSymbolLayer(svgBase64)
        symbol.setSize(6)
        symbol.setFillColor(QColor("#a76dad"))
        symbol.setStrokeWidth(0)
        layer.renderer().symbol().changeSymbolLayer(0, symbol)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # dateTime
        idx = layer.fields().indexFromName("dateTime")
        cfg = {
            "allow_null": False,
            "calendar_popup": False,
            "display_format": (
                "dd/MM/yyyy HH:mm:ss "  # last space needed to avoid timezone
            ),
            "field_format": "yyyy-MM-dd HH:mm:ss",
            "field_iso_format": False,
        }
        setup = QgsEditorWidgetSetup("DateTime", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # platform
        idx = layer.fields().indexFromName("plateformId")
        cfg = {
            "AllowMulti": False,
            "AllowNull": True,
            "Description": "plateform",
            "FilterExpression": " current_value('shipName') =  \"ship\" ",
            "Key": "fid",
            "Layer": self.plateformLayer.layer.id(),
            "LayerName": self.plateformLayer.name,
            "LayerProviderName": "ogr",
            "LayerSource": self.plateformLayer.uri,
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "plateform",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, False)
        layer.setEditFormConfig(form_config)
        layer.setFieldAlias(idx, "plateform")

        # transect
        idx = layer.fields().indexFromName("transectId")
        cfg = {
            "AllowMulti": False,
            "AllowNull": True,
            "Description": "transect",
            "Key": "fid",
            "Layer": self.transectLayer.layer.id(),
            "LayerName": self.transectLayer.name,
            "LayerProviderName": "ogr",
            "LayerSource": self.transectLayer.uri,
            "NofColumns": 1,
            "OrderByValue": False,
            "UseCompleter": False,
            "Value": "transect",
        }
        setup = QgsEditorWidgetSetup("ValueRelation", cfg)
        layer.setEditorWidgetSetup(idx, setup)
        form_config = layer.editFormConfig()
        form_config.setReadOnly(idx, False)
        layer.setEditFormConfig(form_config)
        layer.setFieldAlias(idx, "transect")

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

        # speed
        idx = layer.fields().indexFromName("speed")
        cfg = {
            "AllowNull": False,
            "Max": 30,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # course
        idx = layer.fields().indexFromName("courseAverage")
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
        layer.setFieldAlias(idx, "windDir")

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
        layer.setFieldAlias(idx, "swellDir")

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
        layer.setFieldAlias(idx, "cloud")

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

        # subjective
        idx = layer.fields().indexFromName("subjectiveMam")
        cfg = {}
        cfg["map"] = [
            {"EE": "EE"},
            {"EG": "EG"},
            {"GE": "GE"},
            {"EM": "EM"},
            {"ME": "ME"},
            {"EP": "EP"},
            {"PE": "PE"},
            {"GG": "GG"},
            {"GM": "GM"},
            {"MG": "MG"},
            {"GP": "GP"},
            {"PG": "PG"},
            {"MM": "MM"},
            {"MP": "MP"},
            {"PM": "PM"},
            {"PP": "PP"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # subjective
        idx = layer.fields().indexFromName("subjectiveBirds")
        cfg = {}
        cfg["map"] = [
            {"EE": "EE"},
            {"EG": "EG"},
            {"GE": "GE"},
            {"EM": "EM"},
            {"ME": "ME"},
            {"EP": "EP"},
            {"PE": "PE"},
            {"GG": "GG"},
            {"GM": "GM"},
            {"MG": "MG"},
            {"GP": "GP"},
            {"PG": "PG"},
            {"MM": "MM"},
            {"MP": "MP"},
            {"PM": "PM"},
            {"PP": "PP"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # n observers
        idx = layer.fields().indexFromName("nObservers")
        cfg = {
            "AllowNull": False,
            "Max": 4,
            "Min": 0,
            "Precision": 0,
            "Step": 1,
            "Style": "SpinBox",
        }
        setup = QgsEditorWidgetSetup("Range", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # camera
        idx = layer.fields().indexFromName("camera")
        cfg = {}
        cfg["map"] = [{"ON": "ON"}, {"OFF": "OFF"}]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

        # soundFile, soundStart, soundEnd, dateTime
        for field in [
            "soundFile",
            "soundStart",
            "soundEnd",
            "dateTime",
            "validated",
            "survey",
            "cycle",
            "session",
            "shipName",
            "computer",
            "transect",
            "strateType",
            "length",
            "plateformHeight",
            "_effortGroup",
        ]:
            idx = layer.fields().indexFromName(field)
            form_config = layer.editFormConfig()
            form_config.setReadOnly(idx, True)
            if field not in ["dateTime", "validated"]:
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

        # glare severity
        idx = layer.fields().indexFromName("status")
        cfg = {}
        cfg["map"] = [
            {"Begin": "Begin"},
            {"Add": "Add"},
        ]
        setup = QgsEditorWidgetSetup("ValueMap", cfg)
        layer.setEditorWidgetSetup(idx, setup)

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
        # routeType, speed, courseAverage
        expr = "@value is NULL"
        style = QgsConditionalStyle(expr)
        style.setBackgroundColor(QColor("orange"))
        for fieldName in ["routeType", "speed", "courseAverage"]:
            style.setName(fieldName)
            layer.conditionalStyles().setFieldStyles(fieldName, [style])

        # glareFrom
        expr = "if (\"glareSever\" = 'none', @value != 0, False)"
        style = QgsConditionalStyle(expr)
        style.setName("glareSever")
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("glareFrom", [style])

        # glareTo
        style = QgsConditionalStyle(expr)
        style.setName("glareTo")
        style.setBackgroundColor(QColor("orange"))
        layer.conditionalStyles().setFieldStyles("glareTo", [style])

        # validated
        style = QgsConditionalStyle("validated")
        style.setName("Validated")
        style.setBackgroundColor(QColor(178, 223, 138))
        layer.conditionalStyles().setRowStyles([style])
