# sammo-boat

SAMMO-Boat is tool for field data acquisition. This data comes from standardized observations performed from oceanographic ships. Its aim is to ease data collection and validation before being archived and provided to scientists.
In particular, this tool is used by the [Megascope](https://www.observatoire-pelagis.cnrs.fr/surveys/by-boat/?lang=en) protocol led by the PELAGIS Observatory (La Rochelle Université - CNRS) to quantify marine mammals, seabirds, turtles, wastes and boats during IFREMER's marine campaigns. This survey provides insight into species distribution and abundance to provide european indicator.

SAMMO-Boat is a QGIS extension that redesigns interface and handles GPS and microphone support. The GPS trace, the effort data and observations are directly seen on the map. Observers focus on animal detection and can quickly fulfill this detection by relying on audio record. This record can be used afterwards to add the missing information and to validate observations according defined standards.

![](https://github.com/hytechimaging/sammo-boat/blob/main/images/interface.png?raw=true)

## Dependencies

Some dependencies are necessary for the plugin to properly work and may be
installed through the `Python Console` of QGIS Desktop with `pip`. If pip is not installed :

```` python
>>> import subprocess
>>> cmd="python -m ensurepip --upgrade".split(" ")
>>> subprocess.run(cmd)
````

And to install the plugin dependencies :

```` python
>>> import pip
>>> pip.main(['install', 'sounddevice'])
>>> pip.main(['install', 'soundfile'])
>>> pip.main(['install', 'pyserial'])
>>> pip.main(['install', 'pywin32']) # Windows exclusively
````

QGIS Desktop needs to be restarted after installing these dependencies.

## Interface

SAMMO-Boat is designed to work with a clean interface. We provide some QGIS customization files in the `profile` folder.

The `admin` profile provides a full QGIS interface while the operator profile removes allmost all QGIS toolbar and menu.

On Linux, you can use the following commandline :

```
--customizationfile path/to/QGISCUSTOMIZATION3_operator.ini --globalsettingsfile path/to/QGIS3_operator.ini
```

or add the following arguments in a shortcut configuration :

```
--customizationfile path/to/QGISCUSTOMIZATION3_operator.ini --globalsettingsfile path/to/QGIS3_operator.ini
```

On Windows, a menu has been added to configure shorcut on the user desktop:

![](https://github.com/hytechimaging/sammo-boat/blob/main/images/profile.png?raw=true)

## User Manual

### Keyboard shorcuts

Some keyboard shortcuts are available in SAMMO-Boat :

- `Ctrl+<` : zoom in canvas
- `Ctrl+>` : zoom out canvas
- `Shift+G` : enable/disable GPS
- `Shift+S` : save all tables manually
- `Shift+E` : add an entity in environment table 
- `Space` : add an entity in sighting table
- `Shift+F` : open follower dialog to add entities in follower table
- `Shift+A` : stop audio recording
- `Ctrl+Z` : undo last operation
- `Ctrl+Shift+Z` : redo last canceled operation

To use Undo / Redo shorcut, you need to click on the table you want to change before pressing the shortcut.

### Tools

#### Save tool

The save tool <img src="https://github.com/hytechimaging/sammo-boat/blob/main/images/pen.png?raw=true" height="30" width="30" /> can be used to manually save all tables.

#### Export tool

The export tool <img src="https://github.com/hytechimaging/sammo-boat/blob/main/images/export.png?raw=true" height="30" width="30" /> allows to export all tables as csv into an output directory.

#### Merge tool

The merge tool <img src="https://github.com/hytechimaging/sammo-boat/blob/main/images/merge.png?raw=true" height="30" width="30" /> can be used to merge two sessions into another.

To use it, fulfill the merge form with the directory of each session to merge and the output directory. The output session will contain each entity of both session. In case of strict identical entity, only one entity is copied. 

#### Sound replay

When a new entity is added, SAMMO-Boat will capture a sound record. To play it again, you can do a right click on the table line and click on `Play`. An audio player will pop up.

![](https://github.com/hytechimaging/sammo-boat/blob/main/images/play_audio.png?raw=true)

## Known issues

#### Map canvas blinking

If the canvas is blinking when the GPS layer is updated, you need to lower the
`Map Update Interval` parameter (in `Settings`) according to the current
rendering time of the canvas.

Tips: by activating the `Map canvas refresh` option, you can see the rendering time
in the log window. Then you just have to indicate a higher value in `Map Update
Interval` spin box.
