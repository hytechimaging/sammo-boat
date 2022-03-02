# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

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
        self.session = session

        self.surveyButton.clicked.connect(self.surveyEdit)
        self.transectButton.clicked.connect(self.surveyEdit)
        self.strateButton.clicked.connect(self.surveyEdit)
        self.plateformButton.clicked.connect(self.surveyEdit)

    def surveyEdit(self):
        if self.sender() == self.surveyButton:
            vl = self.session.surveyLayer
        elif self.sender() == self.transectButton:
            vl = self.session.transectLayer
        elif self.sender() == self.strateButton:
            vl = self.session.strateLayer
        elif self.sender() == self.plateformButton:
            vl = self.session.plateformLayer
        vl.startEditing()
        if not vl.featureCount():
            feat = QgsVectorLayerUtils.createFeature(vl)
            vl.addFeature(feat)
        feat = next(vl.getFeatures())
        iface.openFeatureForm(vl, feat)
        vl.commitChanges()
