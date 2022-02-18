# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path
from qgis.core import (
    QgsAction,
    QgsProject,
    QgsVectorLayer,
    QgsEditorWidgetSetup,
)

from ..database import SammoDataBase

NULL = "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"


class SammoLayer:
    def __init__(
        self,
        db: SammoDataBase,
        table: str,
        name: str,
        soundAction: bool = False,
    ):
        self.db = db
        self.table = table
        self.name = name
        self.soundAction = soundAction

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

        if self.soundAction:
            self.addSoundAction(layer)

        self._hideWidgetFid(layer)
        self._init(layer)

    def _init(self, layer: QgsVectorLayer) -> None:
        pass

    def _hideWidgetFid(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

    def addSoundAction(self, layer: QgsVectorLayer) -> None:
        layer.actions().clearActions()
        with open(Path(__file__).parent / "audio_action.py") as f:
            code = f.read()
        code = code.format(
            (
                Path(__file__).parent.parent.parent.parent
                / "images"
                / "pause.png"
            ).as_posix(),
            (
                Path(__file__).parent.parent.parent.parent
                / "images"
                / "play.png"
            ).as_posix(),
            self.db.directory,
        )

        ac = QgsAction(1, "Play", code, False)
        layer.actions().addAction(ac)
