@echo off
start "QGIS" /B "{{ QGIS_EXECUTABLE }}" --profile admin --customizationfile "{{ PROFILE_PATH }}\QGISCUSTOMIZATION3_admin.ini" --globalsettingsfile "{{ PROFILE_PATH }}\QGIS3_admin.ini"