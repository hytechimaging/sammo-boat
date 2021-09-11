# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from .src.gui.permanents_threads_closer_btn import (
    SammoPermanentsThreadsCloserBtn,
)
from .src.core.gps_extractor import GpsExtractor
from .src.gui.permanents_threads_closer_btn import SammoPermanentsThreadsCloserBtn
from .src.gui.session_btn import SammoActionSession
from .src.gui.on_off_effort_btn import SammoOnOffEffortBtn
from .src.core.session import SammoSession
from .src.gui.add_follower_btn import SammoAddFollowerBtn
from .src.gui.add_observation_btn import SammoAddObservationBtn
from .src.core.thread_simu_gps import ThreadSimuGps
from .src.core.thread_gps_extractor import ThreadGpsExtractor
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature
from .src.gui.simu_gps_btn import SammoSimuGpsBtn
from .src.core.sound_recording_controller import SammoSoundRecordingController
from PyQt5.QtCore import QTimer
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import QgsFeature, QgsProject


class Sammo:
    def __init__(self, iface):
        self.iface = iface
        self._toolBar: QToolBar = self.iface.addToolBar("Sammo ToolBar")
        self._session = SammoSession()
        self._sessionBtn = self.createSessionBtn()
        self._onOffEffortBtn = self.createOnOffEffortBtn()
        self._addFollowerBtn = self.createAddFollowerBtn()
        self._addObservationBtn = self.createAddObservationBtn()
        self._simuGpsBtn, self._threadSimuGps = self.createSimuGps()
        self._soundRecordingController = self.createSoundRecordingController()
        self._threadGpsExtractor = self.createGpsExtractor()
        self._permanentThreadsCloser = self.createPermanentThreadsCloser()
        QgsProject.instance().readProject.connect(self.projectLoaded)
        self.gpsExtractor = GpsExtractor()

    def createSoundRecordingController(self) -> SammoSoundRecordingController:
        controller = SammoSoundRecordingController()
        controller.onStopSoundRecordingForObservationSignal.connect(
            self._session.onStopSoundRecordingForObservation
        )
        return controller

    def createSimuGps(self) -> [SammoSimuGpsBtn, ThreadSimuGps]:
        if not os.environ.get("SAMMO_DEBUG"):
            return [None, None]
        button = SammoSimuGpsBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeSimuGpsStatusSignal.connect(self.onChangeSimuGpsStatus)
        testFilePath = os.path.join(
            self.pluginFolder(), "src", "core", "trace_simu_gps.csv"
        )
        threadGps = ThreadSimuGps(self._session, testFilePath)
        threadGps.addNewFeatureToGpsTableSignal.connect(
            self._session.addNewFeatureToGpsTable
        )
        return [button, threadGps]

    def createPermanentThreadsCloser(self) -> SammoPermanentsThreadsCloserBtn:
        button = SammoPermanentsThreadsCloserBtn(
            self.iface.mainWindow(), self._toolBar
        )
        button.onAskForCloserPermanentsThreadsSignal.connect(
            self.onAskForCloserPermanentsThreads
        )
        return button

    def createGpsExtractor(self) -> ThreadGpsExtractor:
        threadGps = ThreadGpsExtractor(self._session)
        threadGps.addNewFeatureToGpsTableSignal.connect(
            self._session.addNewFeatureToGpsTable
        )
        threadGps.start()
        return threadGps

    @staticmethod
    def pluginFolder():
        return os.path.abspath(os.path.dirname(__file__))

    def createAddFollowerBtn(self) -> SammoAddFollowerBtn:
        button = SammoAddFollowerBtn(self.iface.mainWindow(), self._toolBar)
        button.onClickAddFollowerSignal.connect(self.onClickAddFollower)
        button.onAddFeatureToFollowerTableSignal.connect(
            self.onAddFeatureToFollowerTableSignal
        )
        return button

    def createAddObservationBtn(self) -> SammoAddObservationBtn:
        button = SammoAddObservationBtn(self.iface.mainWindow(), self._toolBar)
        button.onClickObservationSignal.connect(self.onClickObservation)
        return button

    def createOnOffEffortBtn(self) -> SammoOnOffEffortBtn:
        button = SammoOnOffEffortBtn(self.iface.mainWindow(), self._toolBar)
        button.onChangeEffortStatusSignal.connect(self.onChangeEffortStatus)
        button.onAddFeatureToEnvironmentTableSignal.connect(
            self.onAddFeatureToEnvironmentTableSignal
        )
        return button

    def createSessionBtn(self) -> SammoActionSession:
        button = SammoActionSession(self.iface.mainWindow(), self._toolBar)
        button.createSignal.connect(self.onCreateSession)
        return button

    def initGui(self):
        pass

    def unload(self):
        self._threadGpsExtractor.stop()
        if (
            self._threadSimuGps is not None
            and self._threadSimuGps.isProceeding
        ):
            self._threadSimuGps.stop()
        self._soundRecordingController.unload()
        self._sessionBtn.unload()
        self._onOffEffortBtn.unload()
        self._addObservationBtn.unload()
        if self._simuGpsBtn is not None:
            self._simuGpsBtn.unload()

        del self._toolBar

    def onAskForCloserPermanentsThreads(self):
        self._threadGpsExtractor.stop()
        pass

    def onCreateSession(self, workingDirectory: str):
        self._session.onNewSession(workingDirectory)
        self._onOffEffortBtn.onNewSession()
        self._addFollowerBtn.onNewSession()
        self._addObservationBtn.onNewSession()
        self._soundRecordingController.onNewSession(workingDirectory)
        if self._simuGpsBtn:
            self._simuGpsBtn.onNewSession()

    def onChangeEffortStatus(self, isChecked: bool):
        if isChecked:
            (
                feat,
                table,
            ) = self._session.getReadyToAddNewFeatureToEnvironmentTable()
            self._onOffEffortBtn.openFeatureForm(self.iface, table, feat)
        else:
            self._session.onStopEffort()

    def onClickObservation(self):
        self._soundRecordingController.onChangeObservationStatus(True)
        feat, table = self._session.getReadyToAddNewFeatureToObservationTable()
        if self.iface.openFeatureForm(table, feat):
            self._session.addNewFeatureToObservationTable(feat)
            self._soundRecordingController.onChangeObservationStatus(False)

    def onClickAddFollower(self):
        feat, table = self._session.getReadyToAddNewFeatureToFollowerTable()
        self._addFollowerBtn.openFeatureForm(self.iface, table, feat)

    def onAddFeatureToEnvironmentTableSignal(self, feat: QgsFeature):
        self._session.onStartEffort(feat)

    def onAddFeatureToFollowerTableSignal(self, feat: QgsFeature):
        self._session.addNewFeatureToFollowerTable(feat)

    def onChangeSimuGpsStatus(self, isOn: bool):
        if isOn:
            self._threadSimuGps.start()
        else:
            self._threadSimuGps.stop()

    def projectLoaded(self):
        try:
            workingDirectory = QgsProject.instance().readPath("./")
            self._session.onLoadProject(workingDirectory)
            self._onOffEffortBtn.onNewSession()
            self._addFollowerBtn.onNewSession()
            self._addObservationBtn.onNewSession()
            self._soundRecordingController.onNewSession(workingDirectory)
            if self._simuGpsBtn:
                self._simuGpsBtn.onNewSession()
        except IndexError:
            pass
