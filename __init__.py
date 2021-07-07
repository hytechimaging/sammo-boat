# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .sammo import Sammo


def classFactory(iface):
    return Sammo(iface)
