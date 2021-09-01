# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDockWidget, QWidget, QHBoxLayout, QPushButton


class Widget:
    widgetName = "MyDock"

    def __init__(self, iface):
        self.iface = iface
        if not self._isDockWidgetExists():
            self.createDockWidget()

    def createDockWidget(self):
        self.dock = QDockWidget(Widget.widgetName, self.iface.mainWindow())
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dock)

        self.internalWidget = QWidget(self.dock)
        self.dock.setWidget(self.internalWidget)
        self.internalWidget.setLayout(QHBoxLayout())
        for i in range(5):
            self.internalWidget.layout().addWidget(QPushButton("{}".format(i)))

    def _isDockWidgetExists(self) -> bool :
        for dockWidget in self.iface.mainWindow().findChildren(QDockWidget):
            if dockWidget.windowTitle() == Widget.widgetName:
                return True
        return False
