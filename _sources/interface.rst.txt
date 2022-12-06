Interface
=========

.. image:: images/interface.png
	:align: center
	:width: 800

The present capture shows the operator profile that includes only Sammo-boat features.

Toolbar
-------

Most Sammo-boat tools are available in the plugin toolbar.

.. |session| image:: ../../images/session.png
  :height: 18

.. |settings| image:: ../../images/settings.png
  :height: 18

.. |save| image:: ../../images/pen.png
  :height: 18

.. |export| image:: ../../images/export.png
  :height: 18

.. |merge| image:: ../../images/merge.png
  :height: 18

.. |environment| image:: ../../images/environment.png
  :height: 18

.. |sighting| image:: ../../images/sightings.png
  :height: 18

.. |follower| image:: ../../images/seabird.png
  :height: 18

.. _sessionbutton:

1 - |session| Session button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This button allows to open an existing session or create a new session (cf. :ref:`session`)

.. _settingsbutton:

2 - |settings| Settings button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This button allows to open the settings dialog, to configure administrators tables.


.. image:: images/settings_dialog.png
   :align: center
   :width: 400

|

`Survey`, `Transect` and `Strate` buttons open the single entity of their table
which can be modified to fulfill the session metadata.

`Boat` and `Plateform` buttons open their tables dialog as each can contains more
than one entity.

3 - |save| Validation button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. image:: images/validate_button.png
   :align: center
   :width: 400

|

This button provides several features. The main action is used to save the
current session, including all layers and the project. This action can also be
done by using the ``Shift+s`` shortcut.

Futhermore the validation button includes the validation feature, that is used
to flag entities as verified. This feature should be used at the end of the
acquisition day, to check records without being in the rush. By default, it will
validate all records, after checking that environnement records are valids, but
user can also select entities in environment/sightning/follower tables to only
validate these particular entities.

At the end, there is also two filters that can be activated to filter
environment/sightning/follower tables. It can be useful to do the entity check.


4 - |export| Export button
~~~~~~~~~~~~~~~~~~~~~~~~~~

This button is used to export session into csv or gpkg files.

.. image:: images/export_dialog.png

|

User have to mention the export folder and the driver.

5 - |merge| Merge button
~~~~~~~~~~~~~~~~~~~~~~~~

This button is used to merge session. It will open the following dialog :

.. image:: images/merge_dialog.png

|

If there is more than one observer on the boat, this feature can be used to merge
data from two distinct session. The environment/sightning/follower tables will be
merging, avoiding to copy identical entities captured on a previous day. Gps point
will be also decimated to keep only one record per minutes.

6 - |environment| Environment button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This button add a new environment record in the environment table. The focus is
set on the table (11) in order that the user can fulfill the attributes
(cf :ref:`environmenttable`). This action can also be done by using the ``Shift+e``
shortcut.

7 - |sighting| Sighting button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This button add a new sighting record in the sighting table. The focus is
set on the table (12) in order that the user can fulfill the attributes
(cf :ref:`sightingtable`). This action can also be done by using the ``Space``
shortcut.

8 - |follower| Follower button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This button is used to handle follower entities. The main action is used to add
new follower records by opening the follower dialog.

.. image:: images/follower_dialog.png

.. |plus| image:: ../../images/plus.png
  :height: 18

The |plus| button adds a new follower record. The followers added in the same
dialog will have the same timestamp.

This action can also be done by using the ``Shift+f`` shortcut.

The second action is used to open the follower table, so that user can check
records before the validation.

Status Panel
------------

9 - GPS button
~~~~~~~~~~~~~~

.. |gps_ok| image:: ../../images/gps_ok.png
	:height: 32

.. |gps_ko| image:: ../../images/gps_ko.png
	:height: 32

The GPS button is used to enable/disable the GPS. If no GPS is found, a message
box will appear to warn the user. Otherwise |gps_ko| will turn into |gps_ok|.
This action can also be done with the ``Shift+g`` shortcut.

The GPS infos are displayed aside the button. Futhermore, a new gps entity is
created per minut.

10 - Microphone button
~~~~~~~~~~~~~~~~~~~~~~

.. |record_ok| image:: ../../images/record_ok.png
	:height: 32

.. |record_ko| image:: ../../images/record_ko.png
	:height: 32


By adding a environment/sighting/follower entity, the plugin starts recording.
User will notice it by seeing the |record_ko| turning into |record_ok|.
Each entity will be attached with its sound record. By default the record lasts
one minute. If user wants to short it, he can click on the |record_ok| button
to turn it into |record_ko|.


Tables and map
--------------

.. _environmenttable:

11 - Environment table
~~~~~~~~~~~~~~~~~~~~~~

The environment table is used to modify environment entity attributes. Most
attributes are duplicated from the previous entity.

Environment entity describes environmental variables during the session.
To keep trace of different routes, according their ``routeType`` attribute.
A status will be assigned automatically to each entity.

The first status will be ``Begin``, then ``Add`` status will be created for the
next entities until user changes the ``routeType`` attribute. User creates
``Add`` entities if the environmental variables change during the route. When the
user changes the ``routeType`` attributes, it duplicates the previous entity
(``Begin`` or ``Add`` status) and assignes the ``End`` status to the duplica.
Environment status are check before the validation. A dialog should pop-up if 
there is a missing ``Start`` / ``End`` record to inform user. Use the duplicate
action to fix it (cf. :ref:`duplicateaction`).

.. _sightingtable:

12 - Sightning table
~~~~~~~~~~~~~~~~~~~~

The sightning table is used to modify sightning entity attributes. Sighting entity describes an observation made by the operator.

13 - Map canvas
~~~~~~~~~~~~~~~

User can follow the ongoing session on the map canvas. The following tables are
displayed:

.. |gps_symbol| image:: images/gps.svg
  :width: 18

.. |environment_symbol| image:: ../../images/environment_symbol.svg
  :width: 18

.. |sighting_symbol| image:: ../../images/observation_symbol.svg
  :width: 18

.. |follower_symbol| image:: ../../images/seabird_symbol.svg
  :width: 18

- world (as background map)
- |gps_symbol| gps 
- |environment_symbol| environmenent 
- |sighting_symbol| sightning 
- |follower_symbol| follower 
