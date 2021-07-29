# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsPointXY,
    QgsGeometry
)


class DashboadTableInitializer:
    @staticmethod
    def initializeTable(dashboardTable: QgsVectorLayer):
        dashboardTable.startEditing()

        effortTimer_label = QgsFeature(dashboardTable.fields())

        xMax, yMax = 185, 90
        effortTimer_label.setGeometry(QgsGeometry.fromPolygonXY(
            [[QgsPointXY(xMax,yMax), QgsPointXY(-xMax,yMax), QgsPointXY(-xMax,-yMax), QgsPointXY(xMax,-yMax),QgsPointXY(xMax,yMax)]]
        ))
        effortTimer_label.setAttribute("name", "effortTimer_label")
        effortTimer_label.setAttribute("geometry_g", "point_n( @map_extent, 4 )")
        effortTimer_label.setAttribute("txt", "00:42:38")
        effortTimer_label.setAttribute("offset_x", 52)
        effortTimer_label.setAttribute("offset_y", 17)
        effortTimer_label.setAttribute("width", 20)
        effortTimer_label.setAttribute("height", 10)
        effortTimer_label.setAttribute("font_name", "Arial")
        effortTimer_label.setAttribute("font_style", "Regular")
        effortTimer_label.setAttribute("font_color", "#fff701")
        effortTimer_label.setAttribute("font_size", 12)
        effortTimer_label.setAttribute("background", "#1500d2")
        dashboardTable.addFeature(effortTimer_label)

        dashboardTable.commitChanges()
