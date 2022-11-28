# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from pathlib import Path

from qgis.PyQt import uic
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject
from qgis.core import QgsVectorLayerUtils
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog

from ..core import utils
from ..core.session import SammoSession

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / "ui/settings.ui")


class SammoSettingsAction(QObject):
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
        dlg = SammoSettingsDialog(self.session)
        dlg.exec_()


class SammoSettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, session):
        super().__init__()
        self.setupUi(self)
        self.setModal(False)
        self.session = session

        self.surveyButton.clicked.connect(self.surveyEdit)
        self.transectButton.clicked.connect(self.surveyEdit)
        self.strateButton.clicked.connect(self.surveyEdit)
        self.boatButton.clicked.connect(self.surveyEdit)
        self.closeButton.clicked.connect(self.close)

    def surveyEdit(self):
        if self.sender() == self.surveyButton:
            vl = self.session.surveyLayer
        elif self.sender() == self.transectButton:
            vl = self.session.transectLayer
        elif self.sender() == self.strateButton:
            vl = self.session.strateLayer
        elif self.sender() == self.boatButton:
            vl = self.session.boatLayer
        vl.startEditing()
        if not vl.featureCount():
            feat = QgsVectorLayerUtils.createFeature(vl)
            vl.addFeature(feat)
        if vl == self.session.boatLayer:
            self.session.plateformLayer
            dlg = QDialog(self)
            dlg.setWindowTitle(vl.name())
            table = iface.showAttributeTable(vl)
            originDlg = table.parent()
            table.setParent(dlg)
            if originDlg:  # version < 3.28 compatibility
                originDlg.hide()
            dlg.show()
            dlg.destroyed.connect(vl.commitChanges)
            dlg.destroyed.connect(self.session.plateformLayer.commitChanges)
            return
        feat = next(vl.getFeatures())
        iface.openFeatureForm(vl, feat)
        vl.commitChanges()
