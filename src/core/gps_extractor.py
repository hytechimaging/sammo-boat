# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"


from qgis.PyQt.QtCore import pyqtSignal
import serial
import sys
import time

SERIAL_PORT = "/dev/ttyUSB0"
running = True


def isGpggaLine(line: str) -> bool:
    typeOfLine = line[0:6]
    return typeOfLine == "$GPGGA"


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

# test : $GPGGA,122630,4822.4652,N,00435.3043,W,1,12,1.9,111.9,M,50.3,M,,*5E


class GpsExtractor:
    addNewFeatureToGpsTableSignal = pyqtSignal(float, float, str, int)
    SERIAL_PORT = "/dev/ttyUSB0"

    def __init__(
        self
    ):
        super().__init__()
        try:
            self._gps = serial.Serial(SERIAL_PORT, baudrate=4800, timeout=0.5)
            print("Port ouvert")
        except:
            print("Impossible d'ouvrir le port")
            exit()

    def core(self):
        try:
            line = self._gps.readline()
            # print(line)
            # if not line:
            #     return
            # print("before decode : " + line)
            # line = line.decode('UTF-8')
            line = line.decode('cp1250')
            # print(line)
            if not isGpggaLine(line):
                return

            position = getPositionData(line)
            if position[0] != sys.float_info.max:
                print("GPS position : longitude = {} - latitude = {}".format(position[0], position[1]))
            else:
                print("GPS offline")

        except:
            print("GPS extraction failed")
            return
