# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
from PyQt5.QtCore import QObject, Qt
from qgis.PyQt import uic, QtGui, QtWidgets


class Widget(QObject):

    def __init__ (self,iface):
        QObject.__init__(self)
        self.iface = iface
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, "widget.ui")
        print(path)
        self.dock = uic.loadUi(path)
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dock)
        self.dock.setVisible(True)
