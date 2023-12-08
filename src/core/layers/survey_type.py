# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2023 Hytech Imaging"

from qgis.core import QgsVectorLayer

from ..database import (
    SammoDataBase,
    SURVEY_TYPE_TABLE,
)
from .layer import SammoLayer


class SammoSurveyTypeLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, SURVEY_TYPE_TABLE, "Survey_type")

    def _init(self, layer: QgsVectorLayer) -> None:
        self._init_widgets(layer)

    def _init_widgets(self, layer: QgsVectorLayer) -> None:
        pass
