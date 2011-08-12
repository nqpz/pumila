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
Command-line parsing
"""

import sys
from optparse import OptionParser, OptionGroup
import os
import re
from . import core
from . import misc
from . import info

info.add_metadata(misc.get_selfdict(__name__))

class _SimplerOptionParser(OptionParser):
    """A simplified OptionParser"""

    def format_description(self, formatter):
        return self.description

    def format_epilog(self, formatter):
        return self.epilog.strip() + '\n'

    def add_option(self, *args, **kwds):
        try: kwds['help'] = kwds['help'].strip()
        except KeyError: pass
        return OptionGroup.add_option(self, *args, **kwds)

def parse_args(cmdargs=None):
    """
    parse_args(cmdargs: [str] = sys.argv[1:]) -> SoundCore

    Base actions on input from the command line. Create a SoundCore object from
    the given options.
    """

    if cmdargs is None:
        cmdargs = sys.argv[1:]

    parser = _SimplerOptionParser(
        prog=info.program.name,
        usage='Usage: %prog [OPTION]... [INPUTFILE]...',
        version=info.program.version_info,
        description=info.program.description,
        epilog='''
Input images must be in a format supported by pygame, i.e. either PNG, JPEG,
GIF, BMP, TGA, PCX, TIF, LBM, PMB, PGM, PPM, or XPM (or a subset). There is
also limited support for OpenRaster files.

If you specify more than one input file, the generated sounds from each file
will be mixed. Extra options, such as gain, can be given as comma-seperated
KEY=VALUE pairs after a slash after the filename, like
`testdir/test1.png/gain=0.7,min=300 Hz,max=10 kHz'. `gain' must be a number
between 0 and 1, and defaults to 1. `min' and `max' denotes the lowest and
highest frequency and understand units. `min' defaults to 220 Hz, and `max'
defaults to 2200 Hz.

''')

    parser.add_option('-o', '--output-file', dest='outputfile',
                      metavar='FILENAME', help='''

the name of the file that sound output should be written to. '-' means standard
out. File format will be derived from file extension, if possible. Defaults to
'out.wav'.

''', default='out.wav')

    parser.add_option('-O', '--no-output-file', dest='outputfile',
                      action='store_false', help='''

do not output sound to a file.

''')

    parser.add_option('-f', '--output-format', dest='outputformat',
                      metavar='FILEFORMAT', type='choice', choices=['wav'],
                      help='''

the format of the sound output. Choose between the default WAVE format 'wav'
(playable by all audio players) and nothing else.

''')
        
    parser.add_option('-y', '--overwrite-outfile', dest='overwrite',
                      action='store_true', default=False, help='''

When writing to a file, overwrite it if it exists.

''')

    parser.add_option('-p', '--play', dest='play',
                      action='store_true', help='''

play the sound after it has been generated.

''', default=False)

    parser.add_option('-P', '--play-at-once', dest='playatonce',
                      action='store_true', help='''

play the sound while it is being generated. This will most likely result in
poor audio, if any, unless your computer is very fast.

''', default=False)

    parser.add_option('-d', '--pixel-duration', dest='pixelduration',
                      metavar='DURATION', help='''

how much time one vertical pixel should last. Second-based units can be
used. If no unit is used, milliseconds are used. Defaults to 10 ms. Is ignored
if --full-duration is given.

''', default=None)

    parser.add_option('-D', '--full-duration', dest='fullduration',
                      metavar='DURATION', help='''

how much time the entire sound should last.

''', default=None)

    parser.add_option('-c', '--channels', dest='channels',
                      metavar='INTEGER', type='int', help='''

the number of channels. Defaults to 1 (mono).

''', default=1)
    
    parser.add_option('-w', '--sample-width', dest='samplewidth',
                      metavar='BITS', type='int', help='''

the size of a sample. Not applicable with the .pml format. Defaults to 16 bits.

''', default=16)
    
    parser.add_option('-r', '--framerate', dest='framerate',
                      metavar='INTEGER', type='int', help='''

the number of samples in one second. Defaults to 44100 (Hz).

''', default=44100)

    parser.add_option('-q', '--quiet', dest='verbose',
                      action='store_false', help='''

do not print info or show a progressbar.

''', default=True)

    parser.add_option('-G', '--no-progressbar', dest= 'showprogressbar',
                  action= 'store_false', help= '''

do not show a progressbar. This option is not needed if --quiet is
specified. Not showing the progressbar can often speed the process up by more
than 100 milliseconds.

''', default=True)

    parser.add_option('-m', '--add-metadata', dest='metadata', nargs=2,
                      action='append', default=[], metavar='KEY VALUE',
                      help='''

add a key-value metadata set. Meaningful KEY strings include "title", "author",
and "description". This option currently does nothing.

''')

    o, args = parser.parse_args(cmdargs)
        
    o.inputfiles = []
    for x in args:
        if os.path.exists(x):
            o.inputfiles.append(x)
        elif '/' in x:
            path, settings = x.rsplit('/', 1)
            settings = {k: v for k, v in (re.split('\s*=\s*', x)
                                          for x in settings.split(','))}
            o.inputfiles.append((path, settings))
            
    if not o.inputfiles:
        parser.print_help()
        print()
        parser.error('no input file specified')

    return core.SoundCore(*o.inputfiles, channels=o.channels,
                           samplewidth=o.samplewidth, framerate=o.framerate,
                           pixelduration=o.pixelduration,
                           fullduration=o.fullduration, play=o.play,
                           playatonce=o.playatonce, outputfile=o.outputfile,
                           outputformat=o.outputformat, overwrite=o.overwrite,
                           metadata=o.metadata, verbose=o.verbose,
                           showprogressbar=o.showprogressbar)
