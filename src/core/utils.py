# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import os
import platform
from pathlib import Path
from datetime import datetime
from shutil import copytree, rmtree

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QSize, QFile
from qgis.PyQt.QtGui import QIcon, QPixmap


ROOT_DIR = Path(__file__).parent.parent.parent


def path(name: str) -> str:
    return str(ROOT_DIR / "images" / name)


def script(name: str) -> str:
    return str(ROOT_DIR / "scripts" / name)


def profile(name: str) -> str:
    return str(ROOT_DIR / "profile" / name)


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
        admin_template = script("template_admin.bat")
        admin_script = script("sammo_boat_admin.bat")
        operator_template = script("template_operator.bat")
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
                if profile_tag in line:
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
                if profile_tag in line:
                    line = line.replace(profile_tag, profile("operator"))
                lines.append(line)

        with open(operator_script, "w") as f:
            for line in lines:
                f.write(line)

        adminPluginPath = (
            Path(QgsApplication.qgisSettingsDirPath()).parent
            / "admin"
            / "python"
            / "plugins"
            / "sammo-boat"
        )
        adminPluginPath.parent.mkdir(parents=True, exist_ok=True)
        operatorPluginPath = (
            Path(QgsApplication.qgisSettingsDirPath()).parent
            / "operator"
            / "python"
            / "plugins"
            / "sammo-boat"
        )
        operatorPluginPath.mkdir(parents=True, exist_ok=True)
        rmtree(adminPluginPath, ignore_errors=True)
        copytree(ROOT_DIR.as_posix(), adminPluginPath)
        rmtree(operatorPluginPath, ignore_errors=True)
        copytree(ROOT_DIR.as_posix(), operatorPluginPath)

        # admin
        # operator
        link_path = (
            Path(os.environ["HOMEDRIVE"])
            / os.environ["HOMEPATH"]
            / "Desktop"
            / "Sammo-boat-admin.lnk"
        ).as_posix()
        ico = path("environment.ico")
        exe = admin_script
        createShortcut(link_path, exe, ico)

        # operator
        link_path = (
            Path(os.environ["HOMEDRIVE"])
            / os.environ["HOMEPATH"]
            / "Desktop"
            / "Sammo-boat-operator.lnk"
        ).as_posix()
        ico = path("environment.ico")
        exe = operator_script
        createShortcut(link_path, exe, ico)
