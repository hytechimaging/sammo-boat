Action
======

Two actions are created by default in the project session.

Audio play action
-----------------

For each environment/sightning/follower entity, Sammo-boat records an audio track.
This track can be play using the audio play action that is available by doing a right
click on a entity.

.. image:: images/audio_action.png
	:align: center

|

It opens a minimalist audio player to listen the track.

.. image:: images/audio_player.png
	:align: center

|

.. _duplicateaction:

Duplicate action
----------------

This action is used to duplicate a environment/sightning/follower entity. As
the audio player, it is available by doing a right click on a entity.

.. image:: images/duplicate_action.png
	:align: center

|

For the environment table, it opens the following dialog:

.. image:: images/duplicate_env.png
	:align: center

|

User can modify the datetime of the duplicat. From this datetime, the entity
geometry will be determined by interpolating the closest gps points. Futhermore,
user can modify the status and the effortGroup attributes
(cf. :ref:`environmenttable`) in order to fix missing environment entities. Other
attributes can be modified in the environment table.

For sighting and follower tables, it opens the following dialog:

.. image:: images/duplicate_oth.png
	:align: center

|

User can only modify the datetime of the duplicat in order to interpolate geometry
from the closest gps points.