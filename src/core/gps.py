# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import sys
import time
import serial
import platform
from serial import SerialException

from qgis.PyQt.QtCore import pyqtSignal

from .other_thread import WorkerForOtherThread, OtherThread


class WorkerGpsExtractor(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, int, int, int)

    def __init__(self):
        super().__init__()
        self._gps: serial.Serial = None
        self.isGpsOnline: bool = False
        self.idOfPort: int = 0
        self.timeOfLastContact = None

    def _onStart(self):
        pass

    @staticmethod
    def _serialPortPrefix() -> str:
        if platform.system() == "Windows":
            return "COM"
        else:
            return "/dev/ttyUSB"

    def _toDoInsideLoop(self):
        if not self._gps:
            for i in range(0, 9):
                port = "{}{}".format(self._serialPortPrefix(), str(i))
                try:
                    self._gps = serial.Serial(port, baudrate=4800, timeout=0.5)
                    print("Port GPS ouvert sur " + port)
                    break
                except (SerialException, OSError):
                    continue

        if not self._gps:
            time.sleep(1.0)
            print("Impossible d'ouvrir le port GPS")
            return

        try:
            line = self._gps.readline()
            line = line.decode("cp1250")
            if not self.isGpggaLine(line):
                self.toDoIfNotAGpggaLine()
                return
            position = self.getPositionData(line)
            longitude_deg = position[0]
            if longitude_deg != sys.float_info.max:
                self.timeOfLastContact = time.time()
                latitude_deg = position[1]
                h, m, s = self.getDatetime(line)
                self.addNewFeatureToGpsTableSignal.emit(
                    float(longitude_deg), float(latitude_deg), h, m, s
                )
                self.isGpsOnline = True
            else:
                print("GPS offline - position not valid")
                self.isGpsOnline = False
        except Exception:
            self._gps = None
            print("GPS offline - exception when trying to read")
            self.isGpsOnline = False

    def toDoIfNotAGpggaLine(self):
        if self.isGpsOnline and (time.time() - self.timeOfLastContact) > 5:
            # if no contact with the GPS after 5 secondes,
            # we consider that it is offline
            self.isGpsOnline = False
            print("GPS offline - time with no contact too long")

    @staticmethod
    def isGpggaLine(line: str) -> bool:
        typeOfLine = line[0:6]
        return typeOfLine == "$GPGGA"

    @staticmethod
    def getDatetime(line: str) -> (int, int, int):
        # "14_25_00"
        components = line.split(",")
        time = components[1]
        hour = int(time[0:2])
        minutes = int(time[2:4])
        secondes = int(time[4:])
        return hour, minutes, secondes

    @staticmethod
    def getPositionData(line: str) -> (float, float):
        components = line.split(",")
        time = components[1]
        if not time:
            return sys.float_info.max, sys.float_info.max

        latitudeAsTxt = components[2]
        latitude_deg = latitudeAsTxt[0:2]
        latitude_min = latitudeAsTxt[2:]
        latitude = float(latitude_deg) + float(latitude_min) / 60.0
        if components[3] != "N":
            latitude = -latitude

        longitudeAsTxt = components[4]
        longitude_deg = longitudeAsTxt[0:3]
        longitude_min = longitudeAsTxt[3:]
        longitude = float(longitude_deg) + float(longitude_min) / 60.0
        if components[5] != "E":
            longitude = -longitude

        return longitude, latitude


class SammoGpsReader(OtherThread):
    frame = pyqtSignal(float, float, int, int, int)

    def __init__(self):
        super().__init__()
        self.active = False

    def start(self):
        self.worker = WorkerGpsExtractor()
        self.worker.addNewFeatureToGpsTableSignal.connect(self.newFrame)
        super()._start(self.worker)

    def newFrame(
        self,
        longitude: float,
        latitude: float,
        hour: int,
        minute: int,
        sec: int,
    ) -> None:
        if self.active:
            self.frame.emit(longitude, latitude, hour, minute, sec)
