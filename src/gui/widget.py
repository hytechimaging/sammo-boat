# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtGui
from qgis.PyQt.QtWidgets import QDockWidget, QWidget, QGridLayout, QVBoxLayout, QLabel


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
        self.internalWidget.setLayout(QGridLayout())

        gpsWidget = self.createGpsWidget()
        effortLabel = self.createEffortLabel()
        soundRecordingLabel = self.createSoundRecordingLabel()
        self.internalWidget.layout().addWidget(gpsWidget, 0, 0)
        self.internalWidget.layout().addWidget(effortLabel, 0, 1)
        self.internalWidget.layout().addWidget(soundRecordingLabel, 0, 2)

    def createEffortLabel(self) -> QLabel:
        label = QLabel("ON/OFF effort")
        label.setStyleSheet("QLabel { background-color : rgb(150,150,150); color : black; }")
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        myFont= QtGui.QFont()
        myFont.setBold(True)
        label.setFont(myFont)

        return label

    def createSoundRecordingLabel(self) -> QLabel:
        label = QLabel("Recording")
        label.setStyleSheet("QLabel { background-color : rgb(200,255,200); color : black; }")
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        myFont= QtGui.QFont()
        myFont.setBold(True)
        label.setFont(myFont)

        return label

    def createGpsWidget(self) -> QWidget:
        gpsWidget = QWidget(self.dock)
        gpsWidget.setLayout(QVBoxLayout())
        gpsWidget.setStyleSheet("QWidget { background-color : rgb(255,150,150); color : black; }")
        title = QLabel("GPS online")
        title.setAlignment(Qt.AlignCenter)
        myFont= QtGui.QFont()
        myFont.setBold(True)
        title.setFont(myFont)

        gpsWidget.layout().addWidget(title)
        gpsWidget.layout().addWidget(QLabel("Latitude : XXX"))
        gpsWidget.layout().addWidget(QLabel("Longitude : YYY"))

        return gpsWidget

    def _isDockWidgetExists(self) -> bool :
        for dockWidget in self.iface.mainWindow().findChildren(QDockWidget):
            if dockWidget.windowTitle() == Widget.widgetName:
                return True
        return False
