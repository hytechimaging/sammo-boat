# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from ..database import (
    SammoDataBase,
    SPECIES_TABLE,
)

from .layer import SammoLayer


class SammoSpeciesLayer(SammoLayer):
    def __init__(self, db: SammoDataBase):
        super().__init__(db, SPECIES_TABLE, "Species")
