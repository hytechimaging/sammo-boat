# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QListWidget, QDockWidget


class Widget:
    widgetName = "MyDock"

    def __init__(self, iface):
        self.iface = iface
        dockWidgetFound = False
        for dockWidget in self.iface.mainWindow().findChildren(QDockWidget):
            print(dockWidget.windowTitle())
            if dockWidget.windowTitle() == Widget.widgetName:
                dockWidgetFound = True
                print("FOUND !!!!!!!!!!!!!!!")
                break
        if not dockWidgetFound:
            self.createDockWidget()

    def createDockWidget(self):
        self.dock = QDockWidget(Widget.widgetName, self.iface.mainWindow())
        customerList = QListWidget(self.dock)
        items = ["John Doe, Harmony Enterprises, 12 Lakeside, Ambleton",
                 "Jane Doe, Memorabilia, 23 Watersedge, Beaton",
                 "Tammy Shea, Tiblanka, 38 Sea Views, Carlton",
                 "Tim Sheen, Caraba Gifts, 48 Ocean Way, Deal",
                 "Sol Harvey, Chicos Coffee, 53 New Springs, Eccleston",
                 "Sally Hobart, Tiroli Tea, 67 Long River, Fedula"
                 ]
        customerList.addItems(items)
        self.dock.setWidget(customerList)
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dock)
        self.dock.setWindowTitle(Widget.widgetName)
