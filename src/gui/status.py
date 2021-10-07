# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import (
    QFrame,
    QLabel,
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

    def updateRecording(self, status):
        self.record.setStyleSheet(self._styleSheet(status))
        self.record.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "record_ko.png"
        if status:
            icon = "record_ok.png"

        px = pixmap(icon, QSize(64, 64))
        self.record.setPixmap(px)

    def updateEffort(self, status):
        self.effort.setStyleSheet(self._styleSheet(status))
        self.effort.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "effort_ko.png"
        if status:
            icon = "effort_ok.png"

        px = pixmap(icon, QSize(64, 64))
        self.effort.setPixmap(px)

    def updateGps(self, status, latitude="", longitude=""):
        self.gps.setStyleSheet(self._styleSheet(status, True))
        self.gpsFrame.setStyleSheet(self._styleSheet(status, True))
        self.gps.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        icon = "gps_ko.png"
        if status:
            icon = "gps_ok.png"

        px = pixmap(icon, QSize(64, 64))
        self.gps.setPixmap(px)

        if latitude and longitude:
            self.latitude.setText(f"{latitude:.4f}")
            self.longitude.setText(f"{longitude:.4f}")

    def init(self):
        self.updateRecording(False)
        self.updateEffort(False)
        self.updateGps(False)

    def _styleSheet(self, status, frame=False):
        color = KO_COLOR
        if status:
            color = OK_COLOR

        widget = "QLabel"
        if frame:
            widget = "QFrame"

        return f"""
        {widget} {{
            background-color : {color};
            color : rgb(136,136,136);
        }}
        """


class StatusDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("Sammo Status", iface.mainWindow())
        self.setObjectName("Sammo Status")

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

        self._widget.updateGps(not self._isGpsOffline)
        self._widget.updateEffort(self.isEffortOn)
        self._widget.updateRecording(self.isSoundRecordingOn)

    def updateGpsInfo(self, longitude: float, latitude: float):
        self._counter500msWithoutGpsInfo = 0

        if longitude == sys.float_info.max:
            self._onGpsOffline()
        else:
            self._isGpsOffline = False
            self._widget.updateGps(True, latitude, longitude)

    def unload(self):
        self._endThread()

    def _onGpsOffline(self):
        self._isGpsOffline = True
        self._widget.updateGps(False)

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

    def _saveLastLocation(self, location):
        QgsSettings().setValue("Sammo/StatusDock/Location/", int(location))
