# sammo-boat

SAMMO-Boat is tool for field data acquisition. This data comes from standardized observations performed from oceanographic ships. Its aim is to ease data collection and validation before being archived and provided to scientists.
In particular, this tool is used by the [Megascope](https://www.observatoire-pelagis.cnrs.fr/surveys/by-boat/?lang=en) protocol led by the PELAGIS Observatory (La Rochelle Université - CNRS) to quantify marine mammals, seabirds, turtles, wastes and boats during IFREMER's marine campaigns. This survey provides insight into species distribution and abundance to provide european indicator.

SAMMO-Boat is a QGIS extension that redesigns interface and handles GPS and microphone support. The GPS trace, the effort data and observations are directly seen on the map. Observers focus on animal detection and can quickly fulfill this detection by relying on audio record. This record can be used afterwards to add the missing information and to validate observations according defined standards.


## Dependencies

Some dependencies are necessary for the plugin to properly work and may be
installed through the `Python Console` of QGIS Desktop:

```` python
>>> import pip
>>> pip.main(['install', 'sounddevice'])
>>> pip.main(['install', 'soundfile'])
>>> pip.main(['install', 'pyserial'])
````

QGIS Desktop needs to be restarted after installing these dependencies.


## Known issues

#### Map canvas blinking

If the canvas is blinking when the GPS layer is updated, you need to lower the
`Map Update Interval` parameter (in `Settings`) according to the current
rendering time of the canvas.

Tips: by activating the `Map canvas refresh` option, you can see the rendering time
in the log window. Then you just have to indicate a higher value in `Map Update
Interval` spin box.
