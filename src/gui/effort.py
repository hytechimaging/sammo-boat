# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QAction, QToolBar


class SammoEffortAction(QObject):
    onChangeEffortStatusSignal = pyqtSignal(bool)

    def __init__(self, parent: QObject, toolbar: QToolBar):
        super().__init__()
        self.parent = parent
        self.button: QIcon = None
        self.initGui(parent, toolbar)

    @property
    def icon(self):
        d = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(os.path.dirname(d))
        return QIcon(os.path.join(root, "images", "effort.png"))

    @property
    def enable(self):
        return self.button.isEnabled()

    @enable.setter
    def enable(self, status):
        self.button.setEnabled(status)
        self.button.setChecked(False)

    def initGui(self, parent: QObject, toolbar: QToolBar):
        self.button = QAction(parent)
        self.button.setIcon(self.icon)
        self.button.setToolTip("Start/stop effort")
        self.button.triggered.connect(self.onClick)
        self.button.setEnabled(False)
        self.button.setCheckable(True)
        toolbar.addAction(self.button)

    def unload(self):
        del self.button

    def onClick(self):
        self.onChangeEffortStatusSignal.emit(self.button.isChecked())
