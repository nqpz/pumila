
======
pumila
======

pumila is an image-to-sound converter. It transforms variations in color,
brightness, saturation and opacity into different sounds.

License
=======

pumila is free software under the terms of the GNU Affero General Public
License version 3 (or any later version). This is version 0.1.0 of the program.

Contact
=======

The author of pumila is Niels Serup. Bug reports and suggestions should be sent
to ns@metanohi.name for the time being.


Installation
============

Way #1
------
Get the newest version of pumila at
http://metanohi.name/projects/pumila/ or at
http://pypi.python.org/pypi/pumila

Extract pumila from the downloaded file, cd into it and run this in a
terminal::

  # python3 setup.py install

Examples are available in the ``examples`` directory.

Way #2
------
Just run this (requires that you have python3-setuptools installed)::

  # easy_install3 pumila

Note that this will not make any examples available.

Dependencies
============

Python 3.1+
-----------
* For DEB-based distros (Trisquel, Debian, etc.): run ``apt-get install python3``
* For RPM-based distros: run ``yum install python3``
* For other distros: do something similar or get it at
  http://python.org/download/

PyGame
------
Under normal circumstances, you would do something like this:

* For DEB-based distros: run ``apt-get install python-pygame``
* For RPM-based distros: run ``yum install pygame``
* For other distros: do something similar or get it at
  http://pygame.org/download.shtml

However, the PyGame 1.9.1 release doesn't work perfectly with Python 3, which
means you'll have to compile PyGame from svn yourself, see
http://pygame.org/wiki/Compilation

Cython
------
It's best to get the newest version from http://cython.org/ --- pumila works
with v0.15, but earlier versions haven't been tested very much.


Optional, but recommended modules
=================================

progressbar
-----------

* Website: http://code.google.com/p/python-progressbar/
* Installation: Run ``easy_install3 progressbar``.

setproctitle
------------

* Website: http://code.google.com/p/py-setproctitle/
* Installation: Run ``easy_install3 setproctitle``.


Documentation
=============

What affects what::

           bottom <-- frequency --> top
           bright <-- amplitude --> dark
    no saturation <-- amplitude --> full saturation
      transparent <-- amplitude --> opaque

Wave types::

  hue 0 to 90,        red to ······ chartreuse: sine to triangle
  hue 90 to 180,      chartreuse to cyan:       triangle to square
  hue 180 to 270,     cyan to ····· purple:     square to sawtooth
  hue 270 to 360 (0), purple to ··· red:        sawtooth to sine


Use
===

As a command-line tool
----------------------

Run ``pumila`` to use it. Run ``pumila --help`` to see how to use it.

As a module
-----------

To find out how to use it, run::

  $ pydoc3 pumila

And also::

  $ pydoc3 pumila.core
  $ pydoc3 pumila.primitives

And so on.


Examples
--------

There are a few examples in the ``examples`` directory. All example images are
available under the Creative Commons Zero 1.0 license.


Development
===========

pumila uses Git for code management. The newest (and sometimes unstable) code
is available at::

  $ git clone git://gitorious.org/pumila/pumila.git


This document
=============

Copyright (C) 2011 Niels Serup

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and this
notice are preserved.  This file is offered as-is, without any warranty.
