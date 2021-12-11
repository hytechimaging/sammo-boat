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
    OBSERVERS_TABLE,
)

from .layer import SammoLayer


class SammoObserversLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, OBSERVERS_TABLE, "Observers")
