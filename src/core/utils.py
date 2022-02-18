# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from pathlib import Path
from datetime import datetime

from qgis.PyQt.QtCore import QSize, QFile
from qgis.PyQt.QtGui import QIcon, QPixmap


def path(name: str) -> str:
    return str(Path(__file__).parent.parent.parent / "images" / name)


def icon(name: str) -> QIcon:
    return QIcon(path(name))


def pixmap(name: str, size: QSize) -> QPixmap:
    return icon(name).pixmap(size)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def base64File(path: str) -> str:
    path = Path(path)
    if not (path and path.exists()):
        return
    file = QFile(path.as_posix())
    file.open(QFile.ReadOnly)
    return "base64:" + str(file.readAll().toBase64())[2:-1]
