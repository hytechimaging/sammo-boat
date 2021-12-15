# sammo-boat

QGIS Plugin.


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
