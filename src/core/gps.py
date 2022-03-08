# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import sys
import time
import serial
import platform
from typing import Tuple
from serial import SerialException

from qgis.PyQt.QtCore import pyqtSignal

from .other_thread import WorkerForOtherThread, OtherThread


class WorkerGpsExtractor(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(
        float, float, int, int, int, float, float
    )

    def __init__(self):
        super().__init__()
        self._gps: serial.Serial = None
        self.isGpsOnline: bool = False
        self.isGPRMCMode: bool = False
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
                    time.sleep(1.0)
                    self._gps.readline() # flush incomplete line 
                    check = self._gps.readline()
                    assert bool(
                        self.isGpggaLine(check) or self.isGprmcLine(check)
                    )
                    print("Port GPS ouvert sur " + port)
                    break
                except (SerialException, OSError, AssertionError):
                    continue

        if not self._gps:
            time.sleep(1.0)
            return

        try:
            line = self._gps.readline()
            line = line.decode("cp1250")
            if self.isGprmcLine(line):
                self.isGPRMCMode = True
                trame = SammoGprmcTrame(line)
            elif self.isGpggaLine(line) and not self.isGPRMCMode:
                trame = SammoGpggaTrame(line)
            else:
                self.toDoIfNotAGpggaLine()
                return
            position = trame.positionData
            longitude_deg = position[0]
            if longitude_deg != sys.float_info.max:
                self.timeOfLastContact = time.time()
                latitude_deg = position[1]
                h, m, s = trame.dateTime
                speed, course = trame.track
                self.addNewFeatureToGpsTableSignal.emit(
                    float(longitude_deg),
                    float(latitude_deg),
                    h,
                    m,
                    s,
                    speed,
                    course,
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
    def isGprmcLine(line: str) -> bool:
        typeOfLine = line[0:6]
        return typeOfLine == "$GPRMC"


class SammoGpsReader(OtherThread):
    frame = pyqtSignal(float, float, int, int, int, float, float)

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
        speed: float = -9999.0,
        course: float = -9999.0,
    ) -> None:
        if self.active:
            self.frame.emit(
                longitude, latitude, hour, minute, sec, speed, course
            )


class SammoTrame:
    def __init__(self, line):
        self.longitude: float = 0.0
        self.latitude: float = 0.0
        self.hour: int = 0
        self.minute: int = 0
        self.second: int = 0
        self.speed: float = -9999.0
        self.course: float = -9999.0
        self.dateTime = line
        self.positionData = line

    @property
    def dateTime(self) -> Tuple[int, int, int]:
        return self.hour, self.minutes, self.secondes

    @property
    def positionData(self) -> Tuple[float, float]:
        return self.longitude, self.latitude

    @property
    def track(self) -> Tuple[float, float]:
        return self.speed, self.course


class SammoGpggaTrame(SammoTrame):
    def __init__(self, line):
        super().__init__(line)

    @property
    def dateTime(self) -> Tuple[int, int, int]:
        return super().dateTime

    @dateTime.setter
    def dateTime(self, line: str) -> None:
        components = line.split(",")
        time = components[1]
        self.hour = int(time[0:2])
        self.minutes = int(time[2:4])
        self.secondes = int(float(time[4:]))

    @property
    def positionData(self) -> Tuple[float, float]:
        return super().positionData

    @positionData.setter
    def positionData(self, line: str) -> None:
        components = line.split(",")
        time = components[1]
        if not time:
            return sys.float_info.max, sys.float_info.max

        latitudeAsTxt = components[2]
        latitude_deg = latitudeAsTxt[0:2]
        latitude_min = latitudeAsTxt[2:]
        self.latitude = float(latitude_deg) + float(latitude_min) / 60.0
        if components[3] != "N":
            self.latitude = -self.latitude
        longitudeAsTxt = components[4]
        longitude_deg = longitudeAsTxt[0:3]
        longitude_min = longitudeAsTxt[3:]
        self.longitude = float(longitude_deg) + float(longitude_min) / 60.0
        if components[5] != "E":
            self.longitude = -self.longitude

    @property
    def track(self) -> Tuple[float, float]:
        return super().track


class SammoGprmcTrame(SammoTrame):
    def __init__(self, line):
        super().__init__(line)
        self.track = line

    @property
    def dateTime(self) -> Tuple[int, int, int]:
        return super().dateTime

    @dateTime.setter
    def dateTime(self, line: str) -> None:
        components = line.split(",")
        time = components[1]
        self.hour = int(time[0:2])
        self.minutes = int(time[2:4])
        self.secondes = int(float(time[4:]))

    @property
    def positionData(self) -> Tuple[float, float]:
        return super().positionData

    @positionData.setter
    def positionData(self, line: str) -> None:
        components = line.split(",")
        time = components[1]
        if not time:
            return sys.float_info.max, sys.float_info.max

        latitudeAsTxt = components[3]
        latitude_deg = latitudeAsTxt[0:2]
        latitude_min = latitudeAsTxt[2:]
        self.latitude = float(latitude_deg) + float(latitude_min) / 60.0
        if components[4] != "N":
            self.latitude = -self.latitude
        longitudeAsTxt = components[5]
        longitude_deg = longitudeAsTxt[0:3]
        longitude_min = longitudeAsTxt[3:]
        self.longitude = float(longitude_deg) + float(longitude_min) / 60.0
        if components[6] != "E":
            self.longitude = -self.longitude

    @property
    def track(self) -> Tuple[float, float]:
        return super().track

    @track.setter
    def track(self, line) -> None:
        components = line.split(",")
        self.speed = float(components[7])
        self.course = float(components[8])
