# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.3]

### Add

- Add a button to stop sound acquisition
- Add validation process
- Add administrator tables

### Modified

- Ressources as SVG and world map are saved into the db.
- Merge process speed up
- Only one gps point per minut
- Geometry is saved into Environment layer
- Fix geometry in csv export
- Reduce sound quality to reduce file size
- Sound file are saved in a subfolder
- Status routeType is handled automatically
- Fix focus on following table
- Change some label in sightings table

## [v1.1.2] - 2022-01-07

### Add

- Audio dialog to play record
- On adding a entity, the focus is automatically setted on the table line
- Sightings / environment table can be resized independently
- Undo / redo mechanisms
- Export : sightings layer is exported with joined fields of species table
- Export : environment layer is exported with joined fields of observer table (for left/right/center observer)
- `speed` and `course` fields in environment table

### Modified

- Update README.md with main features
- By default, table are sorted by time desc
- Configure `comment` fields without multiline to ease navigation with `Tab`
- Remove almost all default values
- Audio record increase to 1 min (sigthings / environment)
- Remove duplication of the last entity for sightings (except `side` field)
- `angle` field restriction on sighting table
- `direction` field can be null on sighting table
- Restriction of one value between `behavMaM`/`behavBirds`/`behavShip` fields on sighting table
- Restrict duplication of the last entity in followers table in a same dialog
- `species` field changed to lineEdit instead of comboBox in followers table
- Export : X/Y field renamed Lat/Lon
- Conditional style on null forbidden field

### Removed

- `nFollower` field on followers table

-----

## [v1.1.1] - 2021-12-20

### Modified

- Patches the v1.1.0 to avoid typing error for python version 3.8

-----

## [v1.1.0] - 2021-12-17

/!\ Warning: this version only works for python > 3.10, if you use a python > 3.8 use the patched version 1.1.1

### Add

- Map canvas follows the gps last position #70
- Sighting and followers attribute tables are docked in the interface
- Save status mechanism
- Audio replay
- Export database table as csv
- Merge tools between SAMMO-Boat database
- Add .ini files to use SAMMO-Boat in operator/admin profile
- Add keyboard shortcut

### Modified

- Translation fixes
- Layer attribute constraints #67 #68 #69
- Remove side attribute values in the sighting layer form
- SAMMO-Boat log file will always be written in the plugin root folder
- Debug mode

-----

## [v1.0.0] - 2021-10-08

### Add

- GPS integration
- Status dock widget
- Up-to-date data model
- Setup widgets in forms
- Add symbology for sightings and followers layers
- Add world layer in default project
- ON/OFF effort mode with B/A/E status code
- Add some layers in the default project (observers, species, sightings and followers)

### Modified

- Show .gpkg files when selecting the session directory
- Fixes commit/rollback workflow leading to some unexpected error messages

-----

## [v0.0.1] - 2021-09-16

### Add

- Initial release



[v1.1.2]: https://github.com/hytechimaging/sammo-boat/releases/tag/v1.1.2
[v1.1.1]: https://github.com/hytechimaging/sammo-boat/releases/tag/v1.1.1
[v1.1.0]: https://github.com/hytechimaging/sammo-boat/releases/tag/v1.1.0
[v1.0.0]: https://github.com/hytechimaging/sammo-boat/releases/tag/v1.0.0
[v0.0.1]: https://github.com/hytechimaging/sammo-boat/releases/tag/v0.0.1