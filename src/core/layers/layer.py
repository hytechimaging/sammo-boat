# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import QgsProject, QgsVectorLayer, QgsEditorWidgetSetup

from ..database import SammoDataBase


class SammoLayer:
    def __init__(self, db: SammoDataBase, table: str, name: str):
        self.db = db
        self.table = table
        self.name = name

    @property
    def layer(self) -> QgsVectorLayer:
        if QgsProject.instance().mapLayersByName(self.name):
            return QgsProject.instance().mapLayersByName(self.name)[0]

        return QgsVectorLayer(self.db.tableUri(self.table))

    @property
    def uri(self) -> str:
        return self.db.tableUri(self.table)

    def addToProject(self, project: QgsProject) -> None:
        layer = self.layer
        layer.setName(self.name)
        project.addMapLayer(layer)

        self._hideWidgetFid(layer)
        self._init(layer)

    def _init(self, layer: QgsVectorLayer) -> None:
        pass

    def _hideWidgetFid(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)
