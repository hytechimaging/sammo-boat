# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path
from qgis.core import (
    Qgis,
    QgsAction,
    QgsProject,
    QgsVectorLayer,
    QgsEditorWidgetSetup,
)

from ..database import SammoDataBase
from ..utils import qgisVersion

NULL = "{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}"


class SammoLayer:
    def __init__(
        self,
        db: SammoDataBase,
        table: str,
        name: str,
        soundAction: bool = False,
        duplicateAction: bool = False,
    ):
        self.db = db
        self.table = table
        self.name = name
        self.soundAction = soundAction
        self.duplicateAction = duplicateAction

    @property
    def layer(self) -> QgsVectorLayer:
        if QgsProject.instance().mapLayersByName(self.name):
            return QgsProject.instance().mapLayersByName(self.name)[0]
        return QgsVectorLayer(self.db.tableUri(self.table), baseName=self.name)

    @property
    def uri(self) -> str:
        return self.db.tableUri(self.table)

    def addToProject(self, project: QgsProject) -> None:
        layer = self.layer
        layer.setName(self.name)
        project.addMapLayer(layer)

        if self.soundAction:
            self.addSoundAction(layer)
        if self.duplicateAction:
            self.addDuplicateAction(layer)

        self._hideWidgetFid(layer)
        self._init(layer)

        layer.startEditing()
        layer.commitChanges()
        layer.startEditing()

    def _init(self, layer: QgsVectorLayer) -> None:
        pass

    def _hideWidgetFid(self, layer: QgsVectorLayer) -> None:
        # fid
        idx = layer.fields().indexFromName("fid")
        setup = QgsEditorWidgetSetup("Hidden", {})
        layer.setEditorWidgetSetup(idx, setup)

    def addSoundAction(self, layer: QgsVectorLayer) -> None:
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

        major, minor, _ = qgisVersion()
        if 2 < major < 4 and minor < 29:  # Check API break
            ac = QgsAction(1, "Play audio", code, False)
        else:
            ac = QgsAction(
                Qgis.AttributeActionType.GenericPython,
                "Play audio",
                code,
                False,
            )
        ac.setActionScopes({"Field"})
        layer.actions().addAction(ac)

    def addDuplicateAction(self, layer: QgsVectorLayer) -> None:
        with open(Path(__file__).parent / "duplicate_action.py") as f:
            code = f.read()

        major, minor, _ = qgisVersion()
        if 2 < major < 4 and minor < 29:  # Check API break
            ac = QgsAction(1, "Duplicate record", code, False)
        else:
            ac = QgsAction(
                Qgis.AttributeActionType.GenericPython,
                "Duplicate record",
                code,
                False,
            )
        ac.setActionScopes({"Field", "Entity"})
        layer.actions().addAction(ac)
