# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsEditorWidgetSetup,
    QgsAction,
)

from ..database import SammoDataBase


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
            self._addSoundAction(layer)

        self._hideWidgetFid(layer)
        self._init(layer)

    def _init(self, layer: QgsVectorLayer) -> None:
        pass

    def _hideWidgetFid(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

    def _addSoundAction(self, layer: QgsVectorLayer) -> None:
        code = f"""
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play

filename = Path(\"{self.db.directory}\") / "[% soundFile %]"
sound = AudioSegment.from_wav(filename)
play(sound)
        """

        ac = QgsAction(1, "Play", code, False)
        layer.actions().addAction(ac)
