# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsPointXY,
    QgsGeometry
)


class DashboardTableInitializer:
    Invisible_offset_x = -1000
    effortTimer_ID = 1
    effortTimer_offset_x = 50
    soundRecording_ID = 2
    soundRecording_offset_x = 44

    @staticmethod
    def initializeTable(dashboardTable: QgsVectorLayer):
        dashboardTable.startEditing()

        xMax, yMax = 185, 90

        newLabel = QgsFeature(dashboardTable.fields())
        newLabel.setGeometry(QgsGeometry.fromPolygonXY(
            [[QgsPointXY(xMax,yMax), QgsPointXY(-xMax,yMax), QgsPointXY(-xMax,-yMax), QgsPointXY(xMax,-yMax),QgsPointXY(xMax,yMax)]]
        ))
        newLabel.setAttribute("name", "effortTimer_label")
        newLabel.setAttribute("geometry_g", "point_n( @map_extent, 4 )")
        newLabel.setAttribute("txt", "Effort - 00:42:38")
        newLabel.setAttribute("offset_x", DashboardTableInitializer.Invisible_offset_x)
        newLabel.setAttribute("offset_y", 8)
        newLabel.setAttribute("width", 20)
        newLabel.setAttribute("height", 4)
        newLabel.setAttribute("font_name", "Arial")
        newLabel.setAttribute("font_style", "Regular")
        newLabel.setAttribute("font_color", "#fff701")
        newLabel.setAttribute("font_size", 6)
        newLabel.setAttribute("background", "#1500d2")
        dashboardTable.addFeature(newLabel)

        newLabel = QgsFeature(dashboardTable.fields())
        newLabel.setGeometry(QgsGeometry.fromPolygonXY(
            [[QgsPointXY(xMax,yMax), QgsPointXY(-xMax,yMax), QgsPointXY(-xMax,-yMax), QgsPointXY(xMax,-yMax),QgsPointXY(xMax,yMax)]]
        ))
        newLabel.setAttribute("name", "soundRecording_label")
        newLabel.setAttribute("geometry_g", "point_n( @map_extent, 4 )")
        newLabel.setAttribute("txt", "recording ...")
        newLabel.setAttribute("offset_x", DashboardTableInitializer.Invisible_offset_x)
        newLabel.setAttribute("offset_y", 18)
        newLabel.setAttribute("width", 37)
        newLabel.setAttribute("height", 4)
        newLabel.setAttribute("font_name", "Arial")
        newLabel.setAttribute("font_style", "Regular")
        newLabel.setAttribute("font_color", "#fff701")
        newLabel.setAttribute("font_size", 6)
        newLabel.setAttribute("background", "#aa0000")
        dashboardTable.addFeature(newLabel)

        dashboardTable.commitChanges()
