# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

import os.path
import platform
from datetime import datetime

from qgis.PyQt.QtGui import QKeySequence
from qgis.PyQt.QtWidgets import QToolBar, QShortcut, QTableView, QAction

from qgis.core import (
    QgsProject,
    QgsPointXY,
    QgsGeometry,
    QgsExpression,
    QgsApplication,
    QgsFeatureRequest,
)

from .src.core.status import StatusCode
from .src.core.gps import SammoGpsReader
from .src.core.session import SammoSession
from .src.core.utils import shortcutCreation
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.core.sound_recording_controller import (
    RecordType,
    SammoSoundRecordingController,
)

from .src.gui.save import SammoSaveAction
from .src.gui.table import SammoTableDock
from .src.gui.status import SammoStatusDock
from .src.gui.export import SammoExportAction
from .src.gui.session import SammoSessionAction
from .src.gui.simu_gps import SammoSimuGpsAction
from .src.gui.settings import SammoSettingsAction
from .src.gui.sightings import SammoSightingsAction
from .src.gui.environment import SammoEnvironmentAction
from .src.gui.attribute_table import SammoAttributeTable
from .src.gui.merge import SammoMergeAction, SammoMergeDialog
from .src.gui.followers import SammoFollowersAction, SammoFollowersTable


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self.toolbar.setObjectName("Sammo ToolBar")
        self.filterExpr: str = "True"

        self.gps_wait = False
        self.loading = False
        self.session = SammoSession()

        self.sessionAction = self.createSessionAction()
        self.settingsAction = self.createSettingsAction()
        self.saveAction = self.createSaveAction()
        self.exportAction = self.createExportAction()
        self.mergeAction = self.createMergeAction()
        self.toolbar.addSeparator()
        self.environmentAction = self.createEnvironmentAction()
        self.sightingsAction = self.createSightingsAction()
        self.followersAction = self.createFollowersAction()
        (
            self.simuGpsSerialAction,
            self.threadSerialSimuGps,
        ) = self.createSimuGps(True)
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps(False)

        self.soundRecordingController = self.createSoundRecordingController()
        self.gpsReader = self.createGpsReader()
        self.statusDock = SammoStatusDock(iface, self.session)
        self.statusDock.recordInterrupted.connect(
            self.soundRecordingController.interruptRecording
        )
        self.statusDock.activateGPS.connect(self.activateGPS)
        self.tableDock = SammoTableDock(iface)

        iface.projectRead.connect(self.onProjectLoaded)
        iface.newProjectCreated.connect(self.onProjectLoaded)

        self.initShortcuts()
        QgsApplication.instance().focusChanged.connect(self.focusOn)

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    def setEnabled(self, status):
        self.settingsAction.setEnabled(status)
        self.exportAction.setEnabled(status)
        self.statusDock.setEnabled(status)
        self.environmentAction.setEnabled(status)
        self.followersAction.setEnabled(status)
        self.sightingsAction.setEnabled(status)
        self.saveAction.setEnabled(status)

    def createSoundRecordingController(self) -> SammoSoundRecordingController:
        controller = SammoSoundRecordingController()
        controller.onStopSoundRecordingForEventSignal.connect(
            self.onStopSoundRecordingForEvent
        )
        controller.onSoundRecordingStatusChanged.connect(
            self.onSoundRecordingStatusChanged
        )
        return controller

    def createSimuGps(
        self, serial: bool
    ) -> [SammoSimuGpsAction, ThreadSimuGps]:
        if not os.environ.get("SAMMO_DEBUG"):
            return [None, None]
        button = SammoSimuGpsAction(self.mainWindow, self.toolbar, serial)
        if serial:
            button.onChangeSimuGpsStatusSignal.connect(
                self.onChangeSimuGpsSerialStatus
            )
        else:
            button.onChangeSimuGpsStatusSignal.connect(
                self.onChangeSimuGpsStatus
            )
        if serial:
            testFilePath = os.path.join(
                self.pluginFolder(), "src", "core", "gps_serial_simu.csv"
            )
        else:
            testFilePath = os.path.join(
                self.pluginFolder(), "src", "core", "gps_simu.csv"
            )
        threadGps = ThreadSimuGps(self.session, testFilePath)
        return [button, threadGps]

    def createGpsReader(self) -> SammoGpsReader:
        gps = SammoGpsReader()
        gps.start()
        return gps

    def activateGPS(self) -> None:
        self.saveAll()
        reader = self.gpsReader
        if (
            os.environ.get("SAMMO_DEBUG")
            and self.threadSerialSimuGps
            and self.simuGpsSerialAction.button.isChecked()
        ):
            reader = self.threadSerialSimuGps
        elif (
            os.environ.get("SAMMO_DEBUG")
            and self.threadSimuGps
            and self.simuGpsAction.button.isChecked()
        ):
            reader = self.threadSimuGps

        if reader.receivers(reader.frame):
            reader.frame.disconnect(self.onGpsFrame)
            self.statusDock.desactivateGPS()
            if self.session.environmentLayer.featureCount() and next(
                self.session.environmentLayer.getFeatures(
                    QgsFeatureRequest().addOrderBy("dateTime", False)
                )
            )["status"] != StatusCode.display(StatusCode.END):
                self.session.addEnvironmentFeature(StatusCode.END)
                self.tableDock.refresh(
                    self.session.environmentLayer, self.filterExpr
                )
        elif not (reader.worker and reader.worker._gps):
            self.iface.messageBar().pushCritical(
                "No GPS detected", "retry later"
            )
        else:
            reader.frame.connect(self.onGpsFrame)
        self.saveAll()

    def createSaveAction(self) -> SammoSaveAction:
        button = SammoSaveAction(self.mainWindow, self.toolbar)
        button.saveAction.triggered.connect(self.saveAll)
        button.validateAction.triggered.connect(self.validate)
        button.validateFilter.triggered.connect(self.filterTable)
        button.dateFilter.triggered.connect(self.filterTable)
        return button

    def createExportAction(self) -> SammoExportAction:
        button = SammoExportAction(self.mainWindow, self.toolbar, self.session)
        return button

    def createFollowersAction(self):
        button = SammoFollowersAction(self.mainWindow, self.toolbar)
        button.action.triggered.connect(self.onFollowersAction)
        return button

    def createSightingsAction(self) -> SammoSightingsAction:
        button = SammoSightingsAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onSightingsAction)
        return button

    def createEnvironmentAction(self) -> SammoEnvironmentAction:
        button = SammoEnvironmentAction(self.mainWindow, self.toolbar)
        button.updateEnvironment.connect(self.onEnvironmentAction)
        return button

    def createSessionAction(self) -> SammoSessionAction:
        button = SammoSessionAction(self.mainWindow, self.toolbar)
        button.create.connect(self.onCreateSession)
        return button

    def createSettingsAction(self) -> SammoSettingsAction:
        button = SammoSettingsAction(
            self.mainWindow, self.toolbar, self.session
        )
        return button

    def createMergeAction(self) -> SammoSessionAction:
        button = SammoMergeAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onMergeAction)
        return button

    def initGui(self) -> None:
        if platform.system() == "Windows":
            self.shortcutAction = QAction("Create shorcuts")
            self.shortcutAction.triggered.connect(shortcutCreation)
            self.iface.addPluginToMenu("Sammo-Boat", self.shortcutAction)

    def initShortcuts(self) -> None:
        self.gpsShortcut = QShortcut(QKeySequence("Shift+G"), self.mainWindow)
        self.gpsShortcut.activated.connect(self.activateGPS)
        self.environmentShortcut = QShortcut(
            QKeySequence("Shift+E"), self.mainWindow
        )
        self.environmentShortcut.activated.connect(self.onEnvironmentAction)

        self.followersShortcut = QShortcut(
            QKeySequence("Shift+F"), self.mainWindow
        )
        self.followersShortcut.activated.connect(self.onFollowersAction)

        self.sightingsShortcut = QShortcut(
            QKeySequence("Space"), self.mainWindow
        )
        self.sightingsShortcut.activated.connect(self.onSightingsAction)

        self.endSoundShortcut = QShortcut(
            QKeySequence("Shift+A"), self.mainWindow
        )
        self.endSoundShortcut.activated.connect(
            self.soundRecordingController.interruptRecording
        )

        # Avoid shorcut overload and recreate undo/redo shortcut
        self.iface.mainWindow().findChild(QAction, "mActionUndo").setShortcut(
            QKeySequence()
        )
        self.iface.mainWindow().findChild(QAction, "mActionRedo").setShortcut(
            QKeySequence()
        )
        self.undoShortcut = QShortcut(QKeySequence("Ctrl+Z"), self.mainWindow)
        self.undoShortcut.activated.connect(self.undo)

        self.redoShortcut = QShortcut(
            QKeySequence("Ctrl+Shift+Z"), self.mainWindow
        )
        self.redoShortcut.activated.connect(self.redo)

        self.saveShortcut = QShortcut(QKeySequence("Shift+S"), self.mainWindow)
        self.saveShortcut.activated.connect(self.saveAll)

        self.zoomInShortcut = QShortcut(
            QKeySequence("Ctrl+<"), self.mainWindow
        )
        self.zoomInShortcut.activated.connect(self.iface.mapCanvas().zoomIn)
        self.zoomOutShortcut = QShortcut(
            QKeySequence("Ctrl+>"), self.mainWindow
        )
        self.zoomOutShortcut.activated.connect(self.iface.mapCanvas().zoomOut)

    def unload(self):
        self.activateGPS()  # add End environment Status if needed
        self.gpsReader.stop()

        if self.threadSimuGps is not None and self.threadSimuGps.isProceeding:
            self.threadSimuGps.stop()
        if (
            self.threadSerialSimuGps is not None
            and self.threadSerialSimuGps.isProceeding
        ):
            self.threadSerialSimuGps.stop()
        self.soundRecordingController.interruptRecording()
        self.soundRecordingController.unload()
        self.sessionAction.unload()
        self.followersAction.unload()
        self.environmentAction.unload()
        self.sightingsAction.unload()
        if self.simuGpsAction is not None:
            self.simuGpsSerialAction.unload()
            self.simuGpsAction.unload()

        self.statusDock.unload()
        self.tableDock.unload()
        del self.statusDock
        del self.toolbar

    def filterTable(self):
        self.filterExpr = "True"  # To keep advanced filter up in table dock
        if self.saveAction.dateFilter.isChecked():
            begin = datetime.combine(
                datetime.now().date(), datetime.min.time()
            )
            after = datetime.combine(
                datetime.now().date(), datetime.max.time()
            )
            self.filterExpr += (
                " and datetime > to_datetime("
                f"'{begin.isoformat()}') and "
                "datetime < to_datetime("
                f"'{after.isoformat()}')"
            )
        if self.saveAction.validateFilter.isChecked():
            self.filterExpr += " and validated is False"

        self.tableDock.refresh(
            self.session.environmentLayer, self.filterExpr, False
        )
        self.tableDock.refresh(
            self.session.sightingsLayer, self.filterExpr, False
        )

    def saveAll(self) -> None:
        self.session.saveAll()

    def validate(self) -> None:
        self.session.validate()
        self.session.saveAll()
        self.tableDock.refresh(
            self.session.environmentLayer, self.filterExpr, False
        )
        self.tableDock.refresh(
            self.session.sightingsLayer, self.filterExpr, False
        )

    def onGpsFrame(
        self,
        longitude: float,
        latitude: float,
        h: int,
        m: int,
        s: int,
        speed: float = -9999.0,
        course: float = -9999.0,
    ) -> None:
        updated = True
        now = datetime.now()
        gpsNow = datetime(now.year, now.month, now.day, h, m, s)

        if self.session.lastGpsInfo["datetime"] == gpsNow and (
            speed != -9999.0 or course != -9999.0
        ):
            # a GPRMC frame is coming after a GPGGA frame with the same
            # datetime but speed/course are valid
            self.session.lastGpsInfo["gprmc"]["speed"] = speed
            self.session.lastGpsInfo["gprmc"]["course"] = course
            self.session.lastGpsInfo["gprmc"]["datetime"] = now
        elif self.session.lastGpsInfo["datetime"] != gpsNow:
            # a newer GPRMC/GPGGA frame is coming
            self.session.lastGpsInfo["geometry"] = QgsGeometry.fromPointXY(
                QgsPointXY(longitude, latitude)
            )
            self.session.lastGpsInfo["datetime"] = gpsNow
            if (
                speed != -9999.0
                or course != -9999.0
                or (
                    gpsNow - self.session.lastGpsInfo["gprmc"]["datetime"]
                ).total_seconds()
                > 59
            ):
                self.session.lastGpsInfo["gprmc"]["speed"] = speed
                self.session.lastGpsInfo["gprmc"]["course"] = course
                self.session.lastGpsInfo["gprmc"]["datetime"] = now
        else:
            # we don't need to update GPS info in status panel (offline status
            # is managed internally by the panel)
            updated = False

        if (
            not self.session.lastCaptureTime
            or (gpsNow - self.session.lastCaptureTime).total_seconds() > 59
        ):
            # Wait for one more frame in case we retrieve the speed/course at
            # the next frame. Worst case scenario: we lose 1 frame in database
            if (
                self.session.lastGpsInfo["gprmc"]["speed"] == -9999.0
                and self.session.lastGpsInfo["gprmc"]["course"] == -9999.0
            ):
                # False -> True: speed/course are invalid so we want to wait 1
                # more frame
                # True -> False: speed/course are invalid but we already waited
                # for another frame.
                self.gps_wait = not self.gps_wait
            else:
                # speed/course are valid so we don't need to wait for another
                # frame to come
                self.gps_wait = False

            # we udpate the database if we don't need to wait for speed/course
            if not self.gps_wait:
                self.session.addGps(
                    longitude, latitude, h, m, s, speed, course
                )
                self.session.lastCaptureTime = gpsNow

        # Panel status is updated only if neccessary. This check is necessary
        # because if we receive a GPGGA after a GPRMC for the same datetime,
        # then speed/course are not valid in this call (so we don't want to
        # update the panel).
        if updated:
            self.iface.mapCanvas().setCenter(QgsPointXY(longitude, latitude))
            self.statusDock.updateGpsInfo(
                longitude,
                latitude,
                self.session.lastGpsInfo["gprmc"]["speed"],
                self.session.lastGpsInfo["gprmc"]["course"],
            )

    def onCreateSession(self, sessionDirectory: str) -> None:
        # init session
        self.loading = True
        QgsProject.instance().clear()
        self.session.init(sessionDirectory)
        self.session.saveAll()
        self.loading = False

        self.gpsReader.active = True
        self.setEnabled(True)

        self.soundRecordingController.onNewSession(sessionDirectory)

        self.tableDock.clean()
        self.tableDock.init(
            self.session.environmentLayer, self.session.sightingsLayer
        )
        self.exportAction.session = self.session
        QgsProject.instance().layerWillBeRemoved.connect(self.cleanTableDock)

        # init simu
        if self.simuGpsAction:
            self.simuGpsSerialAction.onNewSession()
            self.simuGpsAction.onNewSession()

    def cleanTableDock(self, layerId):
        if layerId == self.session.environmentLayer.id():
            self.tableDock.removeTable(self.session.environmentLayer.name())
        elif layerId == self.session.sightingsLayer.id():
            self.tableDock.removeTable(self.session.sightingsLayer.name())

    def focusOn(self, old, new) -> None:
        # Set the active on attribute table focus, to use undo/redo action
        if not new:
            return
        if self.tableDock.widget():
            tables = self.tableDock.widget().tables
            if (
                "Environment" in tables
                and new
                == self.tableDock.widget()
                .tables["Environment"]
                .findChild(QTableView, "mTableView")
            ):
                self.iface.setActiveLayer(self.session.environmentLayer)
            elif (
                "Sightings" in tables
                and new
                == self.tableDock.widget()
                .tables["Sightings"]
                .findChild(QTableView, "mTableView")
            ):
                self.iface.setActiveLayer(self.session.sightingsLayer)

    def undo(self):
        self.iface.activeLayer().undoStack().undo()

    def redo(self):
        self.iface.activeLayer().undoStack().redo()

    def onMergeAction(self) -> None:
        self.mergeDialog = SammoMergeDialog()
        self.mergeDialog.mergeEnded.connect(self.onCreateSession)
        self.mergeDialog.show()

    def onEnvironmentAction(self) -> None:
        self.soundRecordingController.onStartEnvironment()
        self.iface.mapCanvas().setFocus()
        layer = self.session.addEnvironmentFeature()
        self.tableDock.refresh(layer, self.filterExpr)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(60)

    def onSightingsAction(self):
        self.soundRecordingController.onStartSightings()
        self.iface.mapCanvas().setFocus()
        layer = self.session.addSightingsFeature()
        self.tableDock.refresh(layer, self.filterExpr)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(60)

    def onFollowersAction(self, validation: QAction):
        if validation == self.followersAction.followerTable:
            table = SammoAttributeTable.attributeTable(
                self.iface, self.session.followersLayer, self.filterExpr
            )
            table.show()
            return

        self.soundRecordingController.onStartFollowers()

        self.followersTable = SammoFollowersTable(
            self.iface,
            self.session.lastGpsInfo["geometry"],
            self.session.followersLayer,
        )
        self.followersTable.addButton.clicked.connect(self.onFollowersAdd)
        self.followersTable.okButton.clicked.connect(self.onFollowersOk)
        self.followersTable.show()

        self.followersAddShortcut = QShortcut(
            QKeySequence("F"), self.followersTable
        )
        self.followersAddShortcut.activated.connect(self.onFollowersAdd)

    def onFollowersOk(self):
        self.session.saveAll()
        self.followersTable.close()
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(0)

    def onFollowersAdd(self):
        self.session.addFollowersFeature(
            self.followersTable.datetime,
            self.followersTable.geom,
            bool(self.followersTable.rowCount()),
        )
        self.followersTable.refresh()

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self.threadSimuGps.start()
        else:
            self.threadSimuGps.stop()

    def onChangeSimuGpsSerialStatus(self, isOn: bool):
        if isOn:
            self.threadSerialSimuGps.start()
        else:
            self.threadSerialSimuGps.stop()

    def onStopSoundRecordingForEvent(
        self,
        recordType: RecordType,
        soundFile: str,
        soundStart: str,
        soundEnd: str,
    ) -> None:
        saveSound = False

        # ok button from followers panel may be clicked without actually adding
        # features
        if recordType == RecordType.FOLLOWERS:
            lastDatetime = self.followersTable.datetime
            expr = QgsExpression(f"epoch(dateTime) = epoch('{lastDatetime}')")
            request = QgsFeatureRequest(expr)

            for fet in self.session.followersLayer.getFeatures(request):
                saveSound = True
                break
        else:
            saveSound = True

        # saveSound information if necessary
        if saveSound:
            self.session.onStopSoundRecordingForEvent(
                recordType, soundFile, soundStart, soundEnd
            )

    def onSoundRecordingStatusChanged(self, isOn: bool):
        self.statusDock.isSoundRecordingOn = isOn

    def onProjectLoaded(self) -> None:
        if self.loading:
            return
        self.gpsReader.active = False
        self.setEnabled(False)
        sessionDir = SammoSession.sessionDirectory(QgsProject.instance())

        if not sessionDir:
            self.soundRecordingController.interruptRecording()
            self.soundRecordingController.unload()
            self.session = SammoSession()
            self.statusDock.session = self.session
            self.settingsAction.session = self.session
            self.tableDock.clean()
            return

        self.onCreateSession(sessionDir)

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
