#!/usr/bin/env python3

# pumila: convert images to sound waves
# Copyright (C) 2011 Niels Serup

# This file is part of pumila.

# pumila is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pumila is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pumila.  If not, see <http://www.gnu.org/licenses/>.

"""
Core information about program
"""

import os

from . import misc

_selfdict, log = misc.get_selfdict(__name__), misc.newlog('info')


program = misc.AttributeDict(
    'name',               'pumila',
    'version',            misc.PeriodTextTuple(0, 1, 0),
    'description',        'convert images to sound waves',
    'author',             'Niels Serup',
    'author_email',       'ns@metanohi.name',
    'author_with_email',  '{author} <{author_email}>',
    'url',                'http://metanohi.name/projects/pumila/',
    'copyright',          'Copyright (C) 2011  Niels Serup',
    'short_license_name', 'AGPLv3+',
    'short_license',      '''\
License AGPLv3+: GNU AGPL version 3 or later <http://gnu.org/licenses/agpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''',
    'version_info',       '{name} {version.text}\n{copyright}\n{short_license}',
    )

home_dir = os.path.expanduser('~')
localpaths = misc.AttributeDict(
    'dirs', [
        'root',        '.pumila',
        ],
    'files', [
        'logfile',     '{root}/.log',
        ],
    to_apply=lambda p: os.path.normcase(os.path.normpath(
            os.path.join(home_dir, p))),
    apply_what=(str,)
    )

@misc.tryorpass(OSError)
def createlocaldirs():
    for v in localpaths.dirs.values():
        os.makedirs(v)
        yield

misc.setaltlogfile(localpaths.files.logfile)

def add_metadata(globdict):
    globdict['__version__'] = program.version.text
    globdict['__author__'] = program.author_with_email

add_metadata(_selfdict)
