# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2023 Hytech Imaging"

from qgis.core import QgsEditorWidgetSetup, QgsVectorLayer
from ..database import (
    SammoDataBase,
    BEHAVIOUR_SPECIES_TABLE,
)

from .layer import SammoLayer


class SammoBehaviourSpeciesLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, BEHAVIOUR_SPECIES_TABLE, "Behaviour_species")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        pass
