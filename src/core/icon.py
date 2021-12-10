# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon, QPixmap


def path(name: str) -> str:
    return str(Path(__file__).parent.parent.parent / "images" / name)


def icon(name: str) -> QIcon:
    return QIcon(path(name))


def pixmap(name: str, size: QSize) -> QPixmap:
    return icon(name).pixmap(size)
