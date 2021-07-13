# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os.path

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsWkbTypes,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsField,
    QgsFeature,
)


class SammoDataBase:
    DB_NAME = "sammo-boat.gpkg"
    LAYER_NAME = "session data"
    ENVIRONMENT_TABLE_NAME = "environment"
    ENVIRONMENT_COMMENT_FIELD_NAME = "commentaire"
    SPECIES_TABLE_NAME = "species"
    OBSERVATION_TABLE_NAME = "observations"
    FOLLOWER_TABLE_NAME = "followers"
    GPS_TABLE_NAME = "gps"
    GPS_LATITUDE_FIELD_NAME = "Latitude"
    GPS_LONGITUDE_FIELD_NAME = "Longitude"
    GPS_TIME_FIELD_NAME = "leg_heure"

    @staticmethod
    def isDataBaseAvailableInThisDirectory(directory):
        return os.path.isfile(SammoDataBase._pathToDataBase(directory))

    def createEmptyDataBase(self, directory):
        db = self._pathToDataBase(directory)

        self._addTableToDataBaseFile(
            db,
            self._createFieldsForEnvironmentTable(),
            self.ENVIRONMENT_TABLE_NAME,
        )
        self._addTableToDataBaseFile(
            db, self._createFieldsForSpeciesTable(), self.SPECIES_TABLE_NAME
        )
        self._addTableToDataBaseFile(
            db,
            self._createFieldsForObservationTable(),
            self.OBSERVATION_TABLE_NAME,
        )
        self._addTableToDataBaseFile(
            db, self._createFieldsForFollowerTable(), self.FOLLOWER_TABLE_NAME
        )
        self._addTableToDataBaseFile(
            db, self._createFieldsForGpsTable(), self.GPS_TABLE_NAME
        )

    @staticmethod
    def _addTableToDataBaseFile(db: str, fields: QgsFields, tableName: str):
        """
        Create the database and save it as gpkg file

        :param db: path to gpkg file to append to or create
        :param fields: the fields of the table
        :param tableName: the name of the table
        """
        geom = QgsWkbTypes.NoGeometry
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = tableName
        if not os.path.isfile(db):
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteFile
            )
        else:
            opts.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteLayer
            )
        crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        QgsVectorFileWriter.create(
            db,
            fields,
            geom,
            crs,
            QgsCoordinateTransformContext(),
            opts,
            QgsFeatureSink.SinkFlags(),
            None,
            tableName,
        )

    @staticmethod
    def _pathToDataBase(directory: str) -> str:
        return os.path.join(directory, SammoDataBase.DB_NAME)

    def _createFieldsForEnvironmentTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("code_leg", QVariant.Int))
        fields.append(self._createFieldShortText("heure"))
        fields.append(self._createFieldShortText("leg_heure"))
        fields.append(self._createFieldShortText("code_trans"))
        fields.append(QgsField("jour", QVariant.Int))
        fields.append(QgsField("mois", QVariant.Int))
        fields.append(QgsField("an", QVariant.Int))
        fields.append(self._createFieldShortText("activite"))
        fields.append(self._createFieldShortText("plateforme"))
        fields.append(QgsField("cap", QVariant.Double))
        fields.append(QgsField("vitesse", QVariant.Double))
        fields.append(QgsField("N observateurs", QVariant.Int))
        fields.append(self._createFieldShortText("obs_babord"))
        fields.append(self._createFieldShortText("obs_tribord"))
        fields.append(QgsField("ebl_de", QVariant.Double))
        fields.append(QgsField("ebl_a", QVariant.Double))
        fields.append(self._createFieldShortText("ebl_intensite"))
        fields.append(QgsField("vent_vrai_direction", QVariant.Double))
        fields.append(QgsField("vent_vrai_force", QVariant.Int))
        fields.append(QgsField("houle_direction", QVariant.Double))
        fields.append(QgsField("houle_hauteur", QVariant.Double))
        fields.append(QgsField("beaufort", QVariant.Int))
        fields.append(QgsField("nebulosite", QVariant.Int))
        fields.append(self._createFieldShortText("cond_generale"))
        fields.append(QgsField("visibilité", QVariant.Double))
        fields.append(
            self._createFieldShortText(self.ENVIRONMENT_COMMENT_FIELD_NAME)
        )
        fields.append(self._createFieldShortText("Survey"))

        return fields

    @staticmethod
    def getIdOfLastAddedFeature(layer: QgsVectorLayer) -> int:
        maxId = -1
        for feature in layer.getFeatures():
            if feature.id() > maxId:
                maxId = feature.id()

        return maxId

    def _createFieldsForSpeciesTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("code_esp", QVariant.Int))
        fields.append(self._createFieldShortText("nom_latin"))
        fields.append(self._createFieldShortText("type"))
        fields.append(QgsField("cat_group_size", QVariant.Int))
        fields.append(self._createFieldShortText("groupe"))
        fields.append(self._createFieldShortText("Famille"))
        fields.append(self._createFieldShortText("List_sp"))
        fields.append(self._createFieldShortText("liste_especes_potentielles"))
        fields.append(self._createFieldShortText("potential_sp"))
        fields.append(self._createFieldShortText("group_pelgas"))
        fields.append(self._createFieldShortText("nom_commun"))
        fields.append(self._createFieldShortText("nom_anglais"))
        fields.append(self._createFieldShortText("nom_espagnol"))
        fields.append(self._createFieldShortText("phylum_public"))
        fields.append(self._createFieldShortText("classe_public"))
        fields.append(self._createFieldShortText("ordre_public"))
        fields.append(self._createFieldShortText("famille_public"))
        fields.append(self._createFieldShortText("taxon_fr"))
        fields.append(self._createFieldShortText("family_eng"))
        fields.append(self._createFieldShortText("group_eng"))
        fields.append(self._createFieldShortText("id_public"))
        fields.append(self._createFieldShortText("LB_NOM_taxref"))
        fields.append(self._createFieldShortText("NOM_VERN_taxref"))
        fields.append(self._createFieldShortText("NOM_VERN_ENG_taxref"))
        fields.append(self._createFieldShortText("CD_NOM_taxref"))
        fields.append(self._createFieldShortText("APHIA_ID_taxref"))
        fields.append(self._createFieldShortText("REGNE_taxref"))
        fields.append(self._createFieldShortText("PHYLUM_taxref"))
        fields.append(self._createFieldShortText("CLASSE_taxref"))
        fields.append(self._createFieldShortText("ORDRE_taxref"))
        fields.append(self._createFieldShortText("FAMILLE_taxref"))
        fields.append(self._createFieldShortText("R_Caraibes"))

        return fields

    @staticmethod
    def initializeSpeciesTable(speciesTable: QgsVectorLayer):
        speciesTable.startEditing()

        species_1 = QgsFeature(speciesTable.fields())
        species_1.setAttribute("code_esp", 1)
        species_1.setAttribute("nom_commun", "Dauphin commun")
        species_1.setAttribute("nom_latin", "Delphinus delphis")
        species_1.setAttribute("famille", "Delphinidae")
        speciesTable.addFeature(species_1)

        species_2 = QgsFeature(speciesTable.fields())
        species_2.setAttribute("code_esp", 2)
        species_2.setAttribute("nom_commun", "Baleine bleue")
        species_2.setAttribute("nom_latin", "Balaenoptera musculus")
        species_2.setAttribute("famille", "Balaenopteridae")
        speciesTable.addFeature(species_2)

        species_3 = QgsFeature(speciesTable.fields())
        species_3.setAttribute("code_esp", 3)
        species_3.setAttribute("nom_commun", "Mouette rieuse")
        species_3.setAttribute("nom_latin", "Chroicocephalus ridibundus")
        species_3.setAttribute("famille", "Laridés")
        speciesTable.addFeature(species_3)

        speciesTable.commitChanges()

    def _createFieldsForObservationTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("code_leg", QVariant.Int))
        fields.append(self._createFieldShortText("heure"))
        fields.append(self._createFieldShortText("leg_heure"))
        fields.append(self._createFieldShortText("code_esp"))
        fields.append(QgsField("nombre", QVariant.Int))
        fields.append(QgsField("min", QVariant.Int))
        fields.append(QgsField("max", QVariant.Int))
        fields.append(self._createFieldShortText("age"))
        fields.append(QgsField("distance", QVariant.Double))
        fields.append(QgsField("angle", QVariant.Double))
        fields.append(QgsField("route", QVariant.Double))
        fields.append(self._createFieldShortText("cote"))
        fields.append(self._createFieldShortText("cptmt_general"))
        fields.append(self._createFieldShortText("cptmt_groupe"))
        fields.append(self._createFieldShortText("malchance"))
        fields.append(self._createFieldShortText("association"))
        fields.append(self._createFieldShortText("cptmt_MM"))
        fields.append(self._createFieldShortText("cptmt_OIS"))
        fields.append(self._createFieldShortText("cptmt_BAT"))
        fields.append(self._createFieldShortText("comment"))

        return fields

    def _createFieldsForFollowerTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("code_leg", QVariant.Int))
        fields.append(self._createFieldShortText("heure"))
        fields.append(self._createFieldShortText("leg_heure"))
        fields.append(self._createFieldShortText("peche"))
        fields.append(self._createFieldShortText("code_esp"))
        fields.append(QgsField("nombre", QVariant.Int))
        fields.append(self._createFieldShortText("age"))
        fields.append(self._createFieldShortText("interaction"))

        return fields

    def _createFieldsForGpsTable(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField(self.GPS_LATITUDE_FIELD_NAME, QVariant.Double))
        fields.append(QgsField(self.GPS_LONGITUDE_FIELD_NAME, QVariant.Double))
        fields.append(self._createFieldShortText(self.GPS_TIME_FIELD_NAME))
        fields.append(QgsField("code_leg", QVariant.Int))

        return fields

    @staticmethod
    def _createFieldShortText(fieldName) -> QgsField:
        return QgsField(fieldName, QVariant.String, len=50)

    def loadTable(self, directory, tableName) -> QgsVectorLayer:
        db = self._pathToDataBase(directory) + "|layername=" + tableName
        return QgsVectorLayer(db, tableName)
