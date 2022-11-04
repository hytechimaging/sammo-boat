# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"


from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolBar, QToolButton

from ..core import utils


class SammoSaveAction(QObject):
    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.action: QAction = None
        self.initGui(parent, toolbar)

    def setEnabled(self, status):
        self.action.setEnabled(status)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.action = QToolButton(parent)
        self.action.setPopupMode(QToolButton.MenuButtonPopup)
        self.action.setToolButtonStyle(Qt.ToolButtonIconOnly)
        menu = QMenu()

        self.saveAction = QAction(parent)
        self.saveAction.setIcon(utils.icon("pen.png"))
        self.saveAction.setToolTip("Save all")
        self.saveAction.setText("Save all")
        self.validateAction = QAction(parent)
        self.validateAction.setIcon(utils.icon("pen_valid.png"))
        self.validateAction.setToolTip("Validate (all or current selection)")
        self.validateAction.setText("Validate (all or current selection)")
        menu.addAction(self.saveAction)
        menu.addAction(self.validateAction)
        menu.addSeparator()
        self.dateFilter = QAction("Filtre depuis la date courante")
        self.dateFilter.setCheckable(True)
        self.validateFilter = QAction("Filtre par non-identifié")
        self.validateFilter.setCheckable(True)
        menu.addAction(self.dateFilter)
        menu.addAction(self.validateFilter)
        self.action.setMenu(menu)
        self.action.setDefaultAction(self.saveAction)
        self.action.setEnabled(False)
        toolbar.addWidget(self.action)

    def unload(self):
        del self.action
