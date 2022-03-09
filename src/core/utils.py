# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import platform
from pathlib import Path
from datetime import datetime

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QSize, QFile
from qgis.PyQt.QtGui import QIcon, QPixmap


def path(name: str) -> str:
    return str(Path(__file__).parent.parent.parent / "images" / name)


def script(name: str) -> str:
    return str(Path(__file__).parent.parent.parent / "scripts" / name)


def profile(name: str) -> str:
    return str(Path(__file__).parent.parent.parent / "profile" / name)


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


def shortcutCreation():
    if platform.system() == "Windows":
        import win32com.client

        # Windows shortcurt
        def createShortcut(path, exe, ico):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = exe
            shortcut.IconLocation = ico
            shortcut.save()

        # office splash screen
        admin_template = script("template_admin_office.bat")
        admin_script = script("sammo_boat_admin.bat")
        operator_template = script("template_operator_office.bat")
        operator_script = script("sammo_boat_operator.bat")

        lines = []
        exe_tag = "{{ QGIS_EXECUTABLE }}"
        profile_tag = "{{ PROFILE_PATH }}"
        with open(admin_template) as f:
            for line in f:
                if exe_tag in line:
                    line = line.replace(
                        exe_tag, QgsApplication.applicationFilePath()
                    )
                elif profile_tag in line:
                    line = line.replace(profile_tag, profile("admin"))
                lines.append(line)

        with open(admin_script, "w") as f:
            for line in lines:
                f.write(line)

        lines = []
        with open(operator_template) as f:
            for line in f:
                if exe_tag in line:
                    line = line.replace(
                        exe_tag, QgsApplication.applicationFilePath()
                    )
                elif profile_tag in line:
                    line = line.replace(profile_tag, profile("operator"))
                lines.append(line)

        with open(operator_script, "w") as f:
            for line in lines:
                f.write(line)

        # admin
        # operator
        path = (
            Path(os.environ["HOMEDRIVE"])
            / os.environ["HOMEPATH"]
            / "Desktop"
            / "Sammo-boat-admin.lnk"
        ).as_posix()
        ico = path("environment.ico")
        exe = admin_script
        createShortcut(path, exe, ico)

        # operator
        path = (
            Path(os.environ["HOMEDRIVE"])
            / os.environ["HOMEPATH"]
            / "Desktop"
            / "Sammo-boat-operator.lnk"
        ).as_posix()
        ico = path("environment.ico")
        exe = operator_script
        createShortcut(path, exe, ico)
