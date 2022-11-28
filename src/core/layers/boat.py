# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from qgis.core import (
    QgsVectorLayer,
    QgsRelation,
    QgsProject,
)
from ..database import (
    SammoDataBase,
    BOAT_TABLE,
)
from .layer import SammoLayer
from .plateform import SammoPlateformLayer

BOAT_RELATION = "boat_plateform"


class SammoBoatLayer(SammoLayer):
    def __init__(self, db: SammoDataBase, plateformLayer: SammoPlateformLayer):
        super().__init__(db, BOAT_TABLE, "Boat")
        self.plateformLayer = plateformLayer

    def _init(self, layer: QgsVectorLayer) -> None:
        project = QgsProject().instance()
        relationManager = project.relationManager()
        if BOAT_RELATION not in relationManager.relations():
            relation = QgsRelation()
            relation.setId(BOAT_RELATION)
            relation.setName(BOAT_RELATION)
            relation.setReferencedLayer(layer.id())
            relation.setReferencingLayer(self.plateformLayer.layer.id())
            relation.addFieldPair("ship", "name")
            relationManager.addRelation(relation)
        self._init_widgets(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        pass
