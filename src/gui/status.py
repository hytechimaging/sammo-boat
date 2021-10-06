# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import sys

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtWidgets import (
    QFrame,
    QLabel,
    QWidget,
    QVBoxLayout,
    QDockWidget,
)

from qgis.core import QgsSettings

from ..core import pixmap
from ..core.thread_widget import ThreadWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/status.ui")
)

OK_COLOR = "rgb(210, 241, 197)"
KO_COLOR = "rgb(242, 186, 195)"


class StatusWidget(QFrame, FORM_CLASS):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.init()

    def setRecording(self, status):
        self.record.setStyleSheet(self._styleSheet(status))
        self.record.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "record_ko.png"
        if status:
            icon = "record_ok.png"

        px = pixmap(icon, QSize(64,64))
        self.record.setPixmap(px)

    def setEffort(self, status):
        self.effort.setStyleSheet(self._styleSheet(status))
        self.effort.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "effort_ko.png"
        if status:
            icon = "effort_ok.png"

        px = pixmap(icon, QSize(64,64))
        self.effort.setPixmap(px)

    def setGps(self, status):
        self.gps.setStyleSheet(self._styleSheet(status, True))
        self.gpsFrame.setStyleSheet(self._styleSheet(status, True))
        self.gps.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "gps_ko.png"
        if status:
            icon = "gps_ok.png"

        px = pixmap(icon, QSize(64,64))
        self.gps.setPixmap(px)

    def init(self):
        self.setRecording(False)
        self.setEffort(False)
        self.setGps(False)

    def _styleSheet(self, status, frame=False):
        color = KO_COLOR
        if status:
            color = OK_COLOR

        widget = "QLabel"
        if frame:
            widget = "QFrame"

        return f"{widget} {{ background-color : {color}; color : white; }}"


class StatusDock(QDockWidget):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())

        self.iface = iface
        self._gpsTitleLabel: QLabel = None
        self._longitudeLabel: QLabel = None
        self._latitudeLabel: QLabel = None
        self.isEffortOn: bool = False
        self.isSoundRecordingOn: bool = False
        self._isGpsOffline = True
        self._thread = ThreadWidget(self.refresh)
        self._startThread()
        self._counter500msWithoutGpsInfo = 0

        self._widget = None
        self._init(iface.mainWindow())

    def setEnabled(self, status):
        if status:
            location = int(
                QgsSettings().value(
                    "Sammo/StatusDock/Location/",
                    Qt.LeftDockWidgetArea,
                )
            )
            self.setVisible(True)
            self.iface.addDockWidget(location, self)
        else:
            self.iface.removeDockWidget(self)
            self.setVisible(False)

    def refresh(self):
        if not self._widget:
            return

        self._counter500msWithoutGpsInfo = self._counter500msWithoutGpsInfo + 1
        if self._counter500msWithoutGpsInfo > 4:
            self._onGpsOffline()

        self._widget.setGps(not self._isGpsOffline)
        self._widget.setEffort(self.isEffortOn)
        self._widget.setRecording(self.isSoundRecordingOn)

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
        # self._gpsTitleLabel.setText("GPS offline")
        # self._latitudeLabel.setText("Latitude : ---")
        # self._longitudeLabel.setText("Longitude : ---")
        # self._updateGpsWidgetColor()

    def _updateGpsWidgetColor(self):
        if self._isGpsOffline:
            self._gpsWidget.setStyleSheet(self._styleSheet(False))
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

    def _init(self, parent):
        self._widget = StatusWidget(self)

        self.setVisible(False)
        self.dockLocationChanged.connect(self._saveLastLocation)
        self.setWidget(self._widget)

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

        self._gpsWidget.layout().setMargin(0)
        self._gpsWidget.layout().setSpacing(0)

        self.updateGpsLocation(sys.float_info.max, sys.float_info.max)

    def _saveLastLocation(self, location):
        QgsSettings().setValue("Sammo/StatusDock/Location/", int(location))
