# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.PyQt.QtWidgets import QMessageBox
from .database import SammoDataBase
from .logger import Logger
from datetime import datetime
from qgis.core import (
    QgsVectorLayerUtils,
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)


class SammoSession:
    def __init__(self):
        self.db = SammoDataBase()
        self.directoryPath: str = None
        self._environmentTable: QgsVectorLayer = None
        self._speciesTable: QgsVectorLayer = None
        self._observationTable: QgsVectorLayer = None
        self._followerTable: QgsVectorLayer = None
        self._gpsTable: QgsVectorLayer = None
        self._dashboardTable: QgsVectorLayer = None

    @staticmethod
    def isDataBaseAvailable(directory):
        return SammoDataBase.isDataBaseAvailableInThisDirectory(directory)

    def onCreateSession(self, directory: str, dashboardLayer: QgsVectorLayer):
        self.directoryPath = directory
        if not self.isDataBaseAvailable(directory):
            # No geopackage DB in this directory
            self.createEmptyDataBase(directory, dashboardLayer)

        self._environmentTable = self.loadTable(
            SammoDataBase.ENVIRONMENT_TABLE_NAME
        )
        self._speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        self._observationTable = self.loadTable(
            SammoDataBase.OBSERVATION_TABLE_NAME
        )
        self._followerTable = self.loadTable(SammoDataBase.FOLLOWER_TABLE_NAME)
        self._gpsTable = self.loadTable(SammoDataBase.GPS_TABLE_NAME)
        self._dashboardTable = self.loadTable("dashboard")

        if not QgsProject.instance().mapLayersByName(
            SammoDataBase.GPS_TABLE_NAME
        ):
            QgsProject.instance().addMapLayer(self._gpsTable)

    def onStopEffort(self):
        table = self._environmentTable
        table.startEditing()
        idLastAddedFeature = self.db.getIdOfLastAddedFeature(
            self._environmentTable
        )
        field_idx = table.fields().indexOf(
            SammoDataBase.ENVIRONMENT_COMMENT_FIELD_NAME
        )
        dateTimeObj = datetime.now()
        timeOfStopEffort = (
            "End of the Effort at : "
            + "{:02d}".format(dateTimeObj.day)
            + "/"
            + "{:02d}".format(dateTimeObj.month)
            + "/"
            + str(dateTimeObj.year)
            + " "
            + "{:02d}".format(dateTimeObj.hour)
            + ":"
            + "{:02d}".format(dateTimeObj.minute)
            + ":"
            + "{:02d}".format(dateTimeObj.second)
        )
        if not table.changeAttributeValue(
            idLastAddedFeature, field_idx, timeOfStopEffort
        ):
            print("Echec de la modification du champs commentaire")

        table.commitChanges()

    def changeTxtOfDashboardLabel(self, id: int, txt: str):
        table = self._dashboardTable
        table.startEditing()
        field_idx = table.fields().indexOf("txt")
        table.changeAttributeValue(id, field_idx, txt)
        table.commitChanges()

    def changeOffsetsDashboardLabel(self, id: int, offset_x: int):
        table = self._dashboardTable
        table.startEditing()
        field_idx = table.fields().indexOf("offset_x")
        table.changeAttributeValue(id, field_idx, offset_x)
        table.commitChanges()

    def changeBackgroundColorLabel(self, id: int, newColor: str):
        table = self._dashboardTable
        table.startEditing()
        field_idx = table.fields().indexOf("background")
        table.changeAttributeValue(id, field_idx, newColor)
        table.commitChanges()

    def createEmptyDataBase(
        self, directory: str, dashboardLayer: QgsVectorLayer
    ):
        self.db.createEmptyDataBase(directory, dashboardLayer)

        speciesTable = self.loadTable(SammoDataBase.SPECIES_TABLE_NAME)
        SammoDataBase.initializeSpeciesTable(speciesTable)

        dashboardTable = self.loadTable("dashboard")
        SammoDataBase.initializeDashboardTable(dashboardTable)

    def loadTable(self, tableName: str) -> QgsVectorLayer:
        layer = self.db.loadTable(self.directoryPath, tableName)
        if not layer.isValid():
            QMessageBox.critical(
                None,
                "Sammo-Boat plugin",
                "Impossible to read the table " + tableName,
            )
        return layer

    def getReadyToAddNewFeatureToEnvironmentTable(self):
        return self._getReadyToAddNewFeature(self._environmentTable)

    def addNewFeatureToEnvironmentTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._environmentTable)

    def getReadyToAddNewFeatureToObservationTable(
        self,
    ) -> (QgsFeature, QgsVectorLayer):
        return self._getReadyToAddNewFeature(self._observationTable)

    def addNewFeatureToObservationTable(self, feature: QgsFeature):
        self._addNewFeature(feature, self._observationTable)

    def addNewFeatureToGpsTable(
        self, longitude: float, latitude: float, leg_heure: str, code_leg: int
    ):
        self._gpsTable.startEditing()

        feature = QgsFeature(QgsVectorLayerUtils.createFeature(self._gpsTable))
        layerPoint = QgsPointXY(longitude, latitude)
        feature.setGeometry(QgsGeometry.fromPointXY(layerPoint))
        feature.setAttribute("leg_heure", leg_heure)
        feature.setAttribute("code_leg", code_leg)

        self._addNewFeature(feature, self._gpsTable)

    @staticmethod
    def _getReadyToAddNewFeature(
        table: QgsVectorLayer,
    ) -> (QgsFeature, QgsVectorLayer):
        feat = QgsVectorLayerUtils.createFeature(table)
        table.startEditing()
        return feat, table

    @staticmethod
    def _addNewFeature(feature: QgsFeature, table: QgsVectorLayer):
        if not table.addFeature(feature):
            Logger.error("addFeature : échec ")
        if not table.commitChanges():
            Logger.error("_addNewFeatureThreadSafe : échec ")
