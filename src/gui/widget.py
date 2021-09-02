# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import sys

from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtGui
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QLabel,
)
from ..core.thread_widget import ThreadWidget


class Widget:
    widgetName = "MyDock"

    def __init__(self, iface):
        self.iface = iface
        self._effortLabel: QLabel = None
        self._soundRecordingLabel: QLabel = None
        self._gpsTitleLabel: QLabel = None
        self._longitudeLabel: QLabel = None
        self._latitudeLabel: QLabel = None
        self._isClignotantOn: bool = False
        self.isEffortOn: bool = False
        self.isSoundRecordingOn: bool = False
        self._isGpsOffline = True
        self._thread = ThreadWidget(self.onTimer_1sec, self.onTimer_500msec)
        self._startThread()
        self._counter500msWithoutGpsInfo = 0
        # if not self._isDockWidgetExists():
        self._createDockWidget()

    def onTimer_1sec(self):
        pass

    def onTimer_500msec(self):
        if not self._effortLabel:
            return

        self._counter500msWithoutGpsInfo = self._counter500msWithoutGpsInfo + 1
        if self._counter500msWithoutGpsInfo > 4:
            self._onGpsOffline()

        self._isClignotantOn = ~self._isClignotantOn

        if self._isClignotantOn and self.isEffortOn:
            self._effortLabel.setText("Effort ON")
        else:
            self._effortLabel.setText("")

        if self._isClignotantOn and self.isSoundRecordingOn:
            self._soundRecordingLabel.setText("RECORDING")
        else:
            self._soundRecordingLabel.setText("")

    def updateGpsLocation(self, longitude: float, latitude: float):
        self._counter500msWithoutGpsInfo = 0

        if longitude == sys.float_info.max:
            self._onGpsOffline()
        else:
            self._isGpsOffline = False
            self._gpsTitleLabel.setText("GPS online")
            self._latitudeLabel.setText("Latitude : {}°".format(latitude))
            self._longitudeLabel.setText("Longitude : {}°".format(longitude))
            self._updateGpsWidgetColor()

    def unload(self):
        self._endThread()

    def _onGpsOffline(self):
        self._isGpsOffline = True
        self._gpsTitleLabel.setText("GPS offline")
        self._latitudeLabel.setText("Latitude : ---")
        self._longitudeLabel.setText("Longitude : ---")
        self._updateGpsWidgetColor()

    def _updateGpsWidgetColor(self):
        if self._isGpsOffline:
            self._gpsWidget.setStyleSheet(
                "QWidget { background-color : rgb(100,0,0); " "color : red; }"
            )
        else:
            self._gpsWidget.setStyleSheet(
                "QWidget { background-color : rgb(100,0,0); "
                "color : rgb(0,255,0); }"
            )

    def _startThread(self):
        if not self._thread.isProceeding:
            self._thread.start()

    def _endThread(self):
        if self._thread and self._thread.isProceeding:
            self._thread.stop()

    def _createDockWidget(self):
        self.dock = QDockWidget(Widget.widgetName, self.iface.mainWindow())
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dock)

        self.internalWidget = QWidget(self.dock)
        self.dock.setWidget(self.internalWidget)
        self.internalWidget.setLayout(QGridLayout())

        self._createGpsWidget()
        self._effortLabel = self._createEffortLabel()
        self._soundRecordingLabel = self._createSoundRecordingLabel()
        self.internalWidget.layout().addWidget(self._gpsWidget, 0, 0)
        self.internalWidget.layout().addWidget(self._effortLabel, 0, 1)
        self.internalWidget.layout().addWidget(self._soundRecordingLabel, 0, 2)

    def _createEffortLabel(self) -> QLabel:
        label = QLabel("")
        label.setStyleSheet(
            "QLabel { background-color : rgb(150,150,150); color : blue; }"
        )
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        myFont = QtGui.QFont("Arial", 24)
        myFont.setBold(True)
        label.setFont(myFont)

        return label

    def _createSoundRecordingLabel(self) -> QLabel:
        label = QLabel("")
        label.setStyleSheet(
            "QLabel { background-color : rgb(200,255,200); color : red; }"
        )
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        myFont = QtGui.QFont("Arial", 24)
        myFont.setBold(True)
        label.setFont(myFont)

        return label

    def _createGpsWidget(self) -> QWidget:
        self._gpsWidget = QWidget(self.dock)
        self._gpsWidget.setLayout(QVBoxLayout())
        self._updateGpsWidgetColor()
        self._gpsTitleLabel = QLabel()
        self._gpsTitleLabel.setAlignment(Qt.AlignCenter)
        myFont = QtGui.QFont()
        myFont.setBold(True)
        self._gpsTitleLabel.setFont(myFont)

        self._latitudeLabel = QLabel()
        self._longitudeLabel = QLabel()
        self._gpsWidget.layout().addWidget(self._gpsTitleLabel)
        self._gpsWidget.layout().addWidget(self._longitudeLabel)
        self._gpsWidget.layout().addWidget(self._latitudeLabel)

        self.updateGpsLocation(sys.float_info.max, sys.float_info.max)

    def _isDockWidgetExists(self) -> bool:
        for dockWidget in self.iface.mainWindow().findChildren(QDockWidget):
            if dockWidget.windowTitle() == Widget.widgetName:
                return True
        return False
