# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from .other_thread import WorkerForOtherThread, OtherThread
from qgis.PyQt.QtCore import pyqtSignal
from .session import SammoSession
import serial
import sys
import time


# def isGpggaLine(line: str) -> bool:
#     typeOfLine = line[0:6]
#     return typeOfLine == "$GPGGA"





class WorkerGpsExtractor(WorkerForOtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str, int)
    SERIAL_PORT = "/dev/ttyUSB0"

    def __init__(
        self
    ):
        super().__init__()
        self._gps: serial.Serial = None
        self.isGpsOnline: bool = False

    def _onStart(self):
        pass

    def _toDoInsideLoop(self):
        if not self._gps:
            try:
                self._gps = serial.Serial(WorkerGpsExtractor.SERIAL_PORT, baudrate=4800, timeout=0.5)
                print("Port GPS ouvert")
            except:
                self._gps = None
                time.sleep(1.0)
                print("Impossible d'ouvrir le port GPS")
                return

        try:
            line = self._gps.readline()
            line = line.decode('cp1250')
            if not self.isGpggaLine(line):
                return
            position = self.getPositionData(line)
            longitude_deg = position[0]
            if longitude_deg != sys.float_info.max:
                latitude_deg = position[1]
                leg_heure = "23034_14_25_00"
                code_leg = 23034
                print("GPS position : longitude = {} - latitude = {}".format(longitude_deg, latitude_deg))
                self.addNewFeatureToGpsTableSignal.emit(
                    float(longitude_deg), float(latitude_deg), leg_heure, code_leg
                    )
                self.isGpsOnline = True
            else:
                print("GPS offline")
                self.isGpsOnline = False

        except:
            print("read datas failed")
            self.isGpsOnline = False
            return

    @staticmethod
    def isGpggaLine(line: str) -> bool:
        typeOfLine = line[0:6]
        return typeOfLine == "$GPGGA"

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


class ThreadGpsExtractor(OtherThread):
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str, int)

    def __init__(self, session: SammoSession):
        super().__init__()
        self._session: SammoSession = session

    def start(self):
        self.worker = WorkerGpsExtractor()
        self.worker.addNewFeatureToGpsTableSignal.connect(
            self.addNewFeatureToGpsTable
        )
        super()._start(self.worker)

    def addNewFeatureToGpsTable(
        self,
        longitude_deg: float,
        latitude_deg: float,
        leg_heure: str,
        code_leg: int,
    ):
        print("addNewFeatureToGpsTable : longitude_deg="
              + str(longitude_deg)
              + " - latitude_deg="
              + str(latitude_deg)
              )
        self.addNewFeatureToGpsTableSignal.emit(
            longitude_deg, latitude_deg, leg_heure, code_leg
        )
