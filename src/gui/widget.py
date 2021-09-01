# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtGui
from qgis.PyQt.QtWidgets import QDockWidget, QWidget, QGridLayout, QVBoxLayout, QLabel
from ..core.thread_widget import ThreadWidget


class Widget:
    widgetName = "MyDock"

    def __init__(self, iface):
        self.iface = iface
        self._effortLabel: QLabel = None
        self._soundRecordingLabel: QLabel = None
        self._longitudeLabel: QLabel = None
        self._latitudeLabel: QLabel = None
        self._isClignotantOn: bool = False
        self.isEffortOn: bool = False
        self.isSoundRecordingOn: bool = False
        self._thread = ThreadWidget(self.onTimer_1sec, self.onTimer_500msec)
        self._startThread()
        #if not self._isDockWidgetExists():
        self.createDockWidget()

    def onTimer_1sec(self):
        pass

    def onTimer_500msec(self):
        if not self._effortLabel:
            return

        self._isClignotantOn = ~self._isClignotantOn

        if self._isClignotantOn and self.isEffortOn:
            self._effortLabel.setText("Effort ON")
        else:
            self._effortLabel.setText("")

        if self._isClignotantOn and self.isSoundRecordingOn:
            self._soundRecordingLabel.setText("RECORDING")
        else:
            self._soundRecordingLabel.setText("")

    def UpdateGpsLocation(self, longitude: float, latitude: float):
        self._latitudeLabel.setText("Latitude : " + str(latitude))
        self._longitudeLabel.setText("Longitude : " + str(longitude))

    def unload(self):
        self.endThread()

    def endThread(self):
        if self._thread and self._thread.isProceeding:
            self._thread.stop()

    def createDockWidget(self):
        self.dock = QDockWidget(Widget.widgetName, self.iface.mainWindow())
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dock)

        self.internalWidget = QWidget(self.dock)
        self.dock.setWidget(self.internalWidget)
        self.internalWidget.setLayout(QGridLayout())

        gpsWidget = self.createGpsWidget()
        self._effortLabel = self.createEffortLabel()
        self._soundRecordingLabel = self.createSoundRecordingLabel()
        self.internalWidget.layout().addWidget(gpsWidget, 0, 0)
        self.internalWidget.layout().addWidget(self._effortLabel, 0, 1)
        self.internalWidget.layout().addWidget(self._soundRecordingLabel, 0, 2)

    def createEffortLabel(self) -> QLabel:
        label = QLabel("")
        label.setStyleSheet("QLabel { background-color : rgb(150,150,150); color : blue; }")
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        myFont= QtGui.QFont()
        myFont.setBold(True)
        label.setFont(myFont)

        return label

    def createSoundRecordingLabel(self) -> QLabel:
        label = QLabel("")
        label.setStyleSheet("QLabel { background-color : rgb(200,255,200); color : red; }")
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

        self._latitudeLabel = QLabel("Latitude : XXX")
        self._longitudeLabel = QLabel("Longitude : XXX")
        gpsWidget.layout().addWidget(title)
        gpsWidget.layout().addWidget(self._longitudeLabel)
        gpsWidget.layout().addWidget(self._latitudeLabel)

        return gpsWidget

    def _startThread(self):
        if not self._thread.isProceeding:
            self._thread.start()

    def _isDockWidgetExists(self) -> bool :
        for dockWidget in self.iface.mainWindow().findChildren(QDockWidget):
            if dockWidget.windowTitle() == Widget.widgetName:
                return True
        return False
