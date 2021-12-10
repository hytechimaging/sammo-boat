# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path
from datetime import datetime

from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import (
    QgsProject,
    QgsPointXY,
    QgsVectorLayerUtils,
)

from .src.core.gps import SammoGpsReader
from .src.core.session import SammoSession
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.core.sound_recording_controller import SammoSoundRecordingController

from .src.gui.table import TableDock
from .src.gui.status import StatusDock
from .src.gui.session import SammoSessionAction
from .src.gui.simu_gps import SammoSimuGpsAction
from .src.gui.sightings import SammoSightingsAction
from .src.gui.environment import SammoEnvironmentAction
from .src.gui.followers import SammoFollowersAction, SammoFollowersTable


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self.toolbar.setObjectName("Sammo ToolBar")

        self.loading = False
        self.session = SammoSession()

        self.sessionAction = self.createSessionAction()
        self.toolbar.addSeparator()
        self.environmentAction = self.createEnvironmentAction()
        self.sightingsAction = self.createSightingsAction()
        self.followersAction = self.createFollowersAction()
        self.simuGpsAction, self.threadSimuGps = self.createSimuGps()

        self.soundRecordingController = self.createSoundRecordingController()
        self.gpsReader = self.createGpsReader()
        self.statusDock = StatusDock(iface)
        self.tableDock = TableDock(iface)

        iface.projectRead.connect(self.onProjectLoaded)
        iface.newProjectCreated.connect(self.onProjectLoaded)

    @property
    def mainWindow(self):
        return self.iface.mainWindow()

    def setEnabled(self, status):
        self.statusDock.setEnabled(status)
        self.environmentAction.setEnabled(status)
        self.followersAction.setEnabled(status)
        self.sightingsAction.setEnabled(status)

    def createSoundRecordingController(self) -> SammoSoundRecordingController:
        controller = SammoSoundRecordingController()
        controller.onStopSoundRecordingForEventSignal.connect(
            self.session.onStopSoundRecordingForEvent
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

    def initGui(self):
        pass

    def unload(self):
        self.gpsReader.stop()

        if self.threadSimuGps is not None and self.threadSimuGps.isProceeding:
            self.threadSimuGps.stop()
        self.soundRecordingController.unload()
        self.sessionAction.unload()
        self.environmentAction.unload()
        self.sightingsAction.unload()
        if self.simuGpsAction is not None:
            self.simuGpsAction.unload()

        self.statusDock.unload()
        del self.statusDock
        del self.toolbar

    def onGpsFrame(self, longitude, latitude, h, m, s):
        self.session.addGps(longitude, latitude, h, m, s)
        self.iface.mapCanvas().setCenter(QgsPointXY(longitude, latitude))
        self.statusDock.updateGpsInfo(longitude, latitude)

    def onCreateSession(self, sessionDirectory: str) -> None:
        # init session
        self.loading = True
        self.session.init(sessionDirectory)
        self.loading = False

        self.gpsReader.active = True
        self.setEnabled(True)

        self.soundRecordingController.onNewSession(sessionDirectory)

        self.tableDock.init(
            self.session.environmentLayer, self.session.sightingsLayer
        )
        self.tableDock.refresh(self.session.sightingsLayer)
        self.tableDock.refresh(self.session.environmentLayer)

        # init simu
        if self.simuGpsAction:
            self.simuGpsAction.onNewSession()

    def onEnvironmentAction(self, onEnvironment: bool):
        self.soundRecordingController.onStartEnvironment()
        layer = self.session.environmentLayer
        feat = QgsVectorLayerUtils.createFeature(layer)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not layer.isEditable():
            layer.startEditing()
        layer.addFeature(feat)

        self.saveAll()

        self.tableDock.refresh(layer)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord()

    def onSightingsAction(self):
        self.soundRecordingController.onStartSightings()

        layer = self.session.sightingsLayer
        feat = QgsVectorLayerUtils.createFeature(layer)
        feat["dateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not layer.isEditable():
            layer.startEditing()
        layer.addFeature(feat)

        self.saveAll()

        self.tableDock.refresh(layer)
        self.soundRecordingController.onStopEventWhichNeedSoundRecord(10)

    def onFollowersAction(self):
        self.followersTable = SammoFollowersTable(
            self.iface, self.session.followersLayer
        )
        self.followersTable.addButton.clicked.connect(self.onFollowersAdd)
        self.followersTable.okButton.clicked.connect(self.onFollowersOk)
        self.followersTable.show()

    def onFollowersOk(self):
        self.saveAll()
        self.followersTable.close()

    def onFollowersAdd(self):
        layer = self.session.followersLayer
        feat = QgsVectorLayerUtils.createFeature(layer)
        feat["dateTime"] = self.followersTable.datetime

        if not layer.isEditable():
            layer.startEditing()
        layer.addFeature(feat)

        self.saveAll()

        self.followersTable.refresh()

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self.threadSimuGps.start()
        else:
            self.threadSimuGps.stop()

    def onSoundRecordingStatusChanged(self, isOn: bool):
        self.statusDock.isSoundRecordingOn = isOn

    def onProjectLoaded(self) -> None:
        if self.loading:
            return

        self.gpsReader.active = False
        self.setEnabled(False)
        sessionDir = SammoSession.sessionDirectory(QgsProject.instance())

        if not sessionDir:
            return

        self.onCreateSession(sessionDir)

    def saveAll(self) -> None:
        for layer in [
            self.session.environmentLayer,
            self.session.sightingsLayer,
            self.session.followersLayer,
        ]:
            layer.commitChanges()
            layer.startEditing()

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))
