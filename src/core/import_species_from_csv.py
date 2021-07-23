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

        for i in range(1, len(lines)):
            params = [
                '"{}"'.format(x)
                for x in list(
                    csv.reader(
                        [lines[i].strip()], delimiter=",", quotechar='"'
                    )
                )[0]
            ]

            newSpecies = QgsFeature(table.fields())
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "code_esp", params[0]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "nom_latin", params[1]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "type", params[2]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "cat_group_size", params[3]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "groupe", params[4]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "Famille", params[5]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "List_sp", params[6]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "liste_especes_potentielles", params[7]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "potential_sp", params[8]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "group_pelgas", params[9]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "nom_commun", params[10]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "nom_anglais", params[11]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "nom_espagnol", params[12]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "phylum_public", params[13]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "classe_public", params[14]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "ordre_public", params[15]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "famille_public", params[16]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "taxon_fr", params[17]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "family_eng", params[18]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "group_eng", params[19]
            )
            ImportSpeciesFromCsv._setAttributeAsInt(
                newSpecies, "id_public", params[20]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "LB_NOM_taxref", params[21]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "NOM_VERN_taxref", params[22]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "NOM_VERN_ENG_taxref", params[23]
            )
            ImportSpeciesFromCsv._setAttributeAsInt(
                newSpecies, "CD_NOM_taxref", params[24]
            )
            ImportSpeciesFromCsv._setAttributeAsInt(
                newSpecies, "APHIA_ID_taxref", params[25]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "REGNE_taxref", params[26]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "PHYLUM_taxref", params[27]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "CLASSE_taxref", params[28]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "ORDRE_taxref", params[29]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "FAMILLE_taxref", params[30]
            )
            ImportSpeciesFromCsv._setAttributeAsText(
                newSpecies, "R_Caraibes", params[31]
            )

            table.addFeature(newSpecies)

        table.commitChanges()

    @staticmethod
    def _setAttributeAsText(
        feat: QgsFeature, attributeName: str, paramFromCsv: str
    ):
        paramFromCsv = ImportSpeciesFromCsv._removeApostrophes(paramFromCsv)
        if not paramFromCsv:
            # let NULL if the string is empty
            return
        feat.setAttribute(attributeName, paramFromCsv)

    @staticmethod
    def _setAttributeAsInt(
        feat: QgsFeature, attributeName: str, paramFromCsv: str
    ):
        paramFromCsv = ImportSpeciesFromCsv._removeApostrophes(paramFromCsv)
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
    def _removeApostrophes(strValue: str) -> str:
        strLen = len(strValue)
        if strValue[0] == '"' and strValue[strLen - 1] == '"':
            strValue = strValue[1 : strLen - 1]
        return strValue
