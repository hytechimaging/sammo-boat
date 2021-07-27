# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import csv
import os.path
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
)


class ImportSpeciesFromCsv:
    @staticmethod
    def importInto(table: QgsVectorLayer):
        speciesFilePath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "species.csv"
        )
        with open(speciesFilePath) as file:
            lines = file.readlines()

        table.startEditing()

        columnNames = [
            "code_esp",
            "nom_latin",
            "type",
            "cat_group_size",
            "groupe",
            "Famille",
            "List_sp",
            "liste_especes_potentielles",
            "potential_sp",
            "group_pelgas",
            "nom_commun",
            "nom_anglais",
            "nom_espagnol",
            "phylum_public",
            "classe_public",
            "ordre_public",
            "famille_public",
            "taxon_fr",
            "family_eng",
            "group_eng",
            "id_public",
            "LB_NOM_taxref",
            "NOM_VERN_taxref",
            "NOM_VERN_ENG_taxref",
            "CD_NOM_taxref",
            "APHIA_ID_taxref",
            "REGNE_taxref",
            "PHYLUM_taxref",
            "CLASSE_taxref",
            "ORDRE_taxref",
            "FAMILLE_taxref",
            "R_Caraibes",
        ]

        columnsOfIntType = ["id_public", "CD_NOM_taxref", "APHIA_ID_taxref"]

        for line in lines[1:]:
            params = [
                '"{}"'.format(x)
                for x in list(
                    csv.reader([line.strip()], delimiter=",", quotechar='"')
                )[0]
            ]

            newSpecies = QgsFeature(table.fields())

            for index, columnName in enumerate(columnNames):
                if columnName in columnsOfIntType:
                    ImportSpeciesFromCsv._setAttributeAsInt(
                        newSpecies, columnName, params[index]
                    )
                else:
                    ImportSpeciesFromCsv._setAttributeAsText(
                        newSpecies, columnName, params[index]
                    )

            table.addFeature(newSpecies)

        table.commitChanges()

    @staticmethod
    def _setAttributeAsText(
        feat: QgsFeature, attributeName: str, paramFromCsv: str
    ):
        paramFromCsv = ImportSpeciesFromCsv._removeQuotes(paramFromCsv)
        if not paramFromCsv:
            # let NULL if the string is empty
            return
        feat.setAttribute(attributeName, paramFromCsv)

    @staticmethod
    def _setAttributeAsInt(
        feat: QgsFeature, attributeName: str, paramFromCsv: str
    ):
        paramFromCsv = ImportSpeciesFromCsv._removeQuotes(paramFromCsv)
        if not ImportSpeciesFromCsv._isAFloat(paramFromCsv):
            # let NULL if the string is not an integer
            return
        feat.setAttribute(attributeName, int(float(paramFromCsv)))

    @staticmethod
    def _isAFloat(strValue: str) -> bool:
        try:
            float(strValue)
            return True
        except ValueError:
            return False

    @staticmethod
    def _removeQuotes(strValue: str) -> str:
        strLen = len(strValue)
        if strValue[0] == '"' and strValue[strLen - 1] == '"':
            strValue = strValue[1 : strLen - 1]
        return strValue
