# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
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

from .src.core.gps import SammoGpsReader
from .src.core.session import SammoSession
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
from .src.gui.sightings import SammoSightingsAction
from .src.gui.environment import SammoEnvironmentAction
from .src.gui.merge import SammoMergeAction, SammoMergeDialog
from .src.gui.followers import SammoFollowersAction, SammoFollowersTable


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self.toolbar.setObjectName("Sammo ToolBar")

        self.loading = False
        self.session = SammoSession()

        self.sessionAction = self.createSessionAction()
        self.saveAction = self.createSaveAction()
        self.exportAction = self.createExportAction()
        self.mergeAction = self.createMergeAction()
        self.toolbar.addSeparator()
        self.environmentAction = self.createEnvironmentAction()
        self.sightingsAction = self.createSightingsAction()
        self.followersAction = self.createFollowersAction()
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps()

        self.soundRecordingController = self.createSoundRecordingController()
        self.gpsReader = self.createGpsReader()
        self.statusDock = SammoStatusDock(iface, self.session)
        self.statusDock.recordInterrupted.connect(
            self.soundRecordingController.interruptRecording
        )
        self.tableDock = SammoTableDock(iface)

        iface.projectRead.connect(self.onProjectLoaded)
        iface.newProjectCreated.connect(self.onProjectLoaded)

        self.initShortcuts()
        QgsApplication.instance().focusChanged.connect(self.focusOn)

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    def setEnabled(self, status):
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

    def createSimuGps(self) -> [SammoSimuGpsAction, ThreadSimuGps]:
        if not os.environ.get("SAMMO_DEBUG"):
            return [None, None]
        button = SammoSimuGpsAction(self.mainWindow, self.toolbar)
        button.onChangeSimuGpsStatusSignal.connect(self.onChangeSimuGpsStatus)
        testFilePath = os.path.join(
            self.pluginFolder(), "src", "core", "gps_simu.csv"
        )
        threadGps = ThreadSimuGps(self.session, testFilePath)
        threadGps.frame.connect(self.onGpsFrame)
        return [button, threadGps]

    def createGpsReader(self) -> SammoGpsReader:
        gps = SammoGpsReader()
        gps.frame.connect(self.onGpsFrame)
        gps.start()
        return gps

    def createSaveAction(self) -> SammoSaveAction:
        button = SammoSaveAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.saveAll)
        return button

    def createExportAction(self) -> SammoExportAction:
        button = SammoExportAction(self.mainWindow, self.toolbar, self.session)
        return button

    def createFollowersAction(self):
        button = SammoFollowersAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onFollowersAction)
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

    def createMergeAction(self) -> SammoSessionAction:
        button = SammoMergeAction(self.mainWindow, self.toolbar)
        button.triggered.connect(self.onMergeAction)
        return button

    def initGui(self) -> None:
        pass

    def initShortcuts(self) -> None:
        self.environmentShortcut = QShortcut(
            QKeySequence("Shift+E"), self.mainWindow
        )
        self.environmentShortcut.activated.connect(self.onEnvironmentAction)

        self.followersShortcut = QShortcut(
            QKeySequence("Shift+F"), self.mainWindow
        )
        self.followersShortcut.activated.connect(self.onFollowersAction)

        self.sightingsShortcut = QShortcut(
            QKeySequence("Shift+O"), self.mainWindow
        )
        self.sightingsShortcut.activated.connect(self.onSightingsAction)

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

    def unload(self):
        self.gpsReader.stop()

        if self.threadSimuGps is not None and self.threadSimuGps.isProceeding:
            self.threadSimuGps.stop()
        self.soundRecordingController.unload()
        self.sessionAction.unload()
        self.followersAction.unload()
        self.environmentAction.unload()
        self.sightingsAction.unload()
        if self.simuGpsAction is not None:
            self.simuGpsAction.unload()

        self.statusDock.unload()
        del self.statusDock
        del self.toolbar

    def saveAll(self) -> None:
        self.session.saveAll()

    def onGpsFrame(self, longitude, latitude, h, m, s):
        self.session.lastGpsGeom = QgsGeometry.fromPointXY(
            QgsPointXY(longitude, latitude)
        )
        now = datetime.now()
        gpsNow = datetime(now.year, now.month, now.day, h, m, s)
        if (
            not self.session.lastCaptureTime
            or (gpsNow - self.session.lastCaptureTime).total_seconds() > 59
        ):
            self.session.addGps(longitude, latitude, h, m, s)
            self.session.lastCaptureTime = gpsNow
        self.iface.mapCanvas().setCenter(QgsPointXY(longitude, latitude))
        self.statusDock.updateGpsInfo(longitude, latitude)

    def onCreateSession(self, sessionDirectory: str) -> None:
        # init session
        self.loading = True
        self.session.init(sessionDirectory)
        self.session.saveAll()
        self.loading = False

        self.gpsReader.active = True
        self.setEnabled(True)

        self.soundRecordingController.onNewSession(sessionDirectory)

        self.tableDock.init(
            self.session.environmentLayer, self.session.sightingsLayer
        )
        self.exportAction.session = self.session
        QgsProject.instance().layerWillBeRemoved.connect(self.cleanTableDock)

        # init simu
        if self.simuGpsAction:
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
        self.mergeDialog.show()

    def onEnvironmentAction(self) -> None:
        self.soundRecordingController.onStartEnvironment()
        layer = self.session.addEnvironmentFeature()
        self.tableDock.refresh(layer)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(60)

    def onSightingsAction(self):
        self.soundRecordingController.onStartSightings()
        layer = self.session.addSightingsFeature()
        self.tableDock.refresh(layer)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(60)

    def onFollowersAction(self):
        self.soundRecordingController.onStartFollowers()

        self.followersTable = SammoFollowersTable(
            self.iface, self.session.followersLayer
        )
        self.followersTable.addButton.clicked.connect(self.onFollowersAdd)
        self.followersTable.okButton.clicked.connect(self.onFollowersOk)
        self.followersTable.show()

        self.followersAddShortcut = QShortcut(
            QKeySequence("Shift+A"), self.followersTable
        )
        self.followersAddShortcut.activated.connect(self.onFollowersAdd)

    def onFollowersOk(self):
        self.session.saveAll()
        self.followersTable.close()
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(0)

    def onFollowersAdd(self):
        self.session.addFollowersFeature(
            self.followersTable.datetime, bool(self.followersTable.rowCount())
        )
        self.followersTable.refresh()

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self.threadSimuGps.start()
        else:
            self.threadSimuGps.stop()

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
            self.session = SammoSession()
            self.statusDock.session = self.session
            return

        self.onCreateSession(sessionDir)

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
