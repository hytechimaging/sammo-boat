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
    SPECIES_TABLE,
)

from .layer import SammoLayer


class SammoSpeciesLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, SPECIES_TABLE, "Species")

    def _init(self, layer: QgsVectorLayer):
        self._init_widgets(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)
