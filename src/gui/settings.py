# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from pathlib import Path

from qgis.PyQt import uic
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject, QDir, pyqtSignal
from qgis.core import QgsVectorLayerUtils, QgsVectorLayer, QgsFeature
from qgis.PyQt.QtWidgets import (
    QAction,
    QToolBar,
    QDialog,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
)


from ..core import utils
from ..core.session import SammoSession

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / "ui/settings.ui")


class SammoSettingsAction(QObject):
    reloadTables: pyqtSignal = pyqtSignal()
    def __init__(
        self, parent: QObject, toolbar: QToolBar, session: SammoSession
    ):
        super().__init__()
        self.action: QAction = None
        self.session = session
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QAction(parent)
        self.action.triggered.connect(self.show)
        self.action.setIcon(utils.icon("settings.png"))
        self.action.setToolTip("Configure administrator table")
        toolbar.addAction(self.action)

    def show(self):
        self.dlg = SammoSettingsDialog(self.session)
        self.dlg.reloadTables.connect(self.reloadTables)
        self.dlg.show()
        self.dlg.accepted.connect(self.clear)

    def clear(self):
        if self.dlg:
            for dlg in self.dlg.findChildren(QDialog):
                dlg.setParent(None)


class SammoSettingsDialog(QDialog, FORM_CLASS):
    reloadTables: pyqtSignal = pyqtSignal()

    def __init__(self, session):
        super().__init__()
        self.setupUi(self)
        self.setModal(False)
        self.session = session

        self.surveyButton.clicked.connect(self.surveyEdit)
        self.surveyTypeButton.clicked.connect(self.surveyEdit)
        self.transectButton.clicked.connect(self.surveyEdit)
        self.transectImportButton.clicked.connect(self.importTransect)
        self.boatButton.clicked.connect(self.surveyEdit)
        self.plateformButton.clicked.connect(self.surveyEdit)
        self.closeButton.clicked.connect(self.accept)

    def surveyEdit(self):
        if self.sender() == self.surveyButton:
            vl = self.session.surveyLayer
        if self.sender() == self.surveyTypeButton:
            vl = self.session.surveyTypeLayer
        elif self.sender() == self.transectButton:
            vl = self.session.transectLayer
        elif self.sender() == self.plateformButton:
            vl = self.session.plateformLayer
        elif self.sender() == self.boatButton:
            vl = self.session.boatLayer
        vl.startEditing()
        if not vl.featureCount():
            feat = QgsVectorLayerUtils.createFeature(vl)
            vl.addFeature(feat)
        if vl in [
            self.session.surveyTypeLayer,
            self.session.boatLayer,
            self.session.plateformLayer,
            self.session.transectLayer,
        ]:
            dlg = QDialog(self)
            dlg.setModal(True)
            dlg.setWindowTitle(vl.name())
            table = iface.showAttributeTable(vl)
            originDlg = table.parent()
            table.setParent(None)
            hLayout = QHBoxLayout(dlg)
            vLayout = QVBoxLayout()
            hLayout.addLayout(vLayout)
            vLayout.addWidget(table)
            originDlg.hide()
            dlg.show()
            dlg.destroyed.connect(vl.commitChanges)
            dlg.destroyed.connect(self.session.plateformLayer.commitChanges)
            return
        feat = next(vl.getFeatures())
        iface.openFeatureForm(vl, feat)
        vl.commitChanges()

    def importTransect(self):
        transect_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a ogr transect file",
            QDir.currentPath(),
            filter="OGR file (*.shp *.gpkg)",
            options=QFileDialog.DontUseNativeDialog,
        )
        if not transect_path:
            return
        lyr = QgsVectorLayer(transect_path, "importTransect", "ogr")
        lyr.geometryType()
        if lyr.geometryType() != 1:  # not Linestring
            iface.messageBar().pushWarning(
                "Geometry Error",
                "Imported transect layer is not a LineString layer, "
                "please provide a LineString layer",
            )
            return
        elif lyr.crs().postgisSrid() != 4326:  # not EPSG:4326:
            iface.messageBar().pushWarning(
                "CRS Error", "Convert the transect layer in EPSG:4326 first"
            )
            return

        self.session.transectLayer.startEditing()
        for importedFt in lyr.getFeatures():
            ft = QgsFeature(self.session.transectLayer.fields())
            ft.setGeometry(importedFt.geometry())
            for field in ft.fields():
                if field.name() == "fid":
                    continue
                elif field.name() in lyr.fields().names():
                    if field.type() is not lyr.fields()[field.name()].type():
                        if field.typeName() == "Integer":
                            value = int(importedFt[field.name()])
                        elif field.typeName() == "Real":
                            value = float(importedFt[field.name()])
                        else:
                            value = importedFt[field.name()]
                    else:
                        value = importedFt[field.name()]
                    ft[field.name()] = value
            self.session.transectLayer.addFeature(ft)
        self.session.transectLayer.commitChanges()
        self.reloadTables.emit()
