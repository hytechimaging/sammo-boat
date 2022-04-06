# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2022 Hytech Imaging"

from enum import Enum


class StatusCode(Enum):
    BEGIN = 0
    ADD = 1
    END = 2

    @staticmethod
    def display(status: "StatusCode") -> str:
        return status.name.capitalize()
