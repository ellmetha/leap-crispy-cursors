leap-crispy-cursors
===================

A set of Leap Motion desktop navigators based on mouse and keyboard events for Linux. Of course, *it is a proof of concept* ; it can be improved (and you are welcome to do it!). Keep in mind that most of desktop environments are not suitable for using the Leap Motion controller as a mouse device.

The mouse cursor is available in two different modes:

- Pitch: the mouse movements are based on the hand pitch, roll and yaw
- Path: the mouse movements are based on the hand path

With each of these modes, you can do other actions like click, press & release, scroll up or down and even switch desktop.


Dependencies
------------

- Leap Motion SDK (https://www.leapmotion.com/developers)
- pymouse and pykeyboard from PyUserInput (https://github.com/SavinaRoja/PyUserInput)
- Python ≥ v2.7


Usage
-----

Run ``python crisoy-cursors.py`` (use ``--help`` to see available options).

- Move your hand above the Leap Motion detection area to move the mouse pointer. The cursor speed is inversely proportional to the number of fingers extended. So you should extend your five fingers in order to execute delicate actions
- Keep your hand on a fixed position during one second to perform a mouse click
- Close your hand in a fist to perform a mouse press and then extend your five fingers to release
- Hold your hand horizontally (with the palm facing down) and extend your five fingers. Then move your fingers up or down to perform a scroll action
- Do a left or right swipe to switch desktop


License
-------

GPLv3. See ``LICENSE.txt`` for more details.
