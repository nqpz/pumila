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
Wrapper for sound generation.
"""

import sys
import os
from fractions import Fraction
import itertools
import re
import numpy
import pygame
import colorsys
import time
import collections
import math
import struct
import wave
try:
    import progressbar
except ImportError:
    progressbar = None

from .generate import SoundGenerator
from . import units
from . import image
from . import primitives
from . import misc
from . import info

_selfdict, log = misc.get_selfdict(__name__), misc.newlog('core')
info.add_metadata(_selfdict)

class SoundCore(SoundGenerator):
    def __init__(self, *inputfiles, channels=1, samplewidth=16, framerate=44100,
                 pixelduration=None, fullduration=None, play=False,
                 playatonce=False, outputfile=None, outputformat=None,
                 overwrite=False, metadata={}, returndata=None, verbose=False,
                 showprogressbar=False):
        """
        Generate sound waves.

        If returndata, return a list of numbers.
        """
        self.inputfiles = []
        for path in inputfiles:
            if isinstance(path, tuple) or isinstance(path, list):
                path, settings = path[0], self.parse_settings(path[1])
            else:
                settings = {}
            if not os.path.isfile(path):
                raise OSError('{} does not exist'.format(repr(path)))
            if not 'gain' in settings:
                settings['gain'] = 1
            if not 'min' in settings:
                settings['min'] = 220
            if not 'max' in settings:
                settings['max'] = 2200
            for x in ('gain', 'min', 'max'):
                if settings[x].denominator == 1:
                    settings[x] = settings[x].numerator
            self.inputfiles.append((path, settings))

        self.channels, self.samplewidth, self.framerate, self.pixelduration, \
            self.fullduration, self.play, self.playatonce, self.outputfile, \
            self.outputformat, self.overwrite, self.metadata, self.returndata, \
            self.verbose, self.showprogressbar = \
            channels, samplewidth, framerate, pixelduration, fullduration, \
            play, playatonce, outputfile, outputformat, overwrite, metadata, \
            returndata, verbose, showprogressbar

        if self.playatonce:
            self.play = True
        if not outputfile and not self.play and returndata is None:
            self.returndata = True
        elif not outputfile and outputformat:
            self.outputformat = None
        elif outputfile:
            if outputformat:
                self.outputformat = outputformat.lower()
            elif outputfile.lower().endswith('.pml'):
                self.outputformat = 'pml'
            else:
                self.outputformat = 'wav' # Default
            if self.outputformat not in ('pml', 'wav'):
                raise ValueError('{} is not an accepted format'.format(
                        self.outputformat))
            if outputfile == '-':
                self.outputfile = open(1, 'wb')
            elif os.path.isfile(outputfile) and not overwrite:
                raise ValueError('file {} already exists'.format(
                        repr(outputfile)))

        if self.pixelduration:
            self.pixelduration = self._unit_parse(self.pixelduration, 'ms')
        if self.fullduration:
            self.fullduration = self._unit_parse(self.fullduration, 'ms')
        elif not self.pixelduration:
            self.pixelduration = 10 # ms, default

        self.log = log if self.verbose else misc.donothing
        if not self.verbose or not progressbar:
            self.showprogressbar = False

    def parse_settings(self, settings):
        """
        parse_settings(settings: dict) -> dict

        Remove pairs where key is not in ('gain', 'min', 'max') and parse units.
        """
        # Warning: a new dict is not created
        for k, v in settings.items():
            if k not in ('gain', 'min', 'max'):
                del settings[k]
            elif k in ('gain', 'min', 'max'):
                val = self._unit_parse(v, 'Hz')
                if val:
                    settings[k] = val
                else:
                    del settings[k]
        return settings

    def _unit_parse(self, val, default_unit=None):
        try:
            return Fraction(val)
        except ValueError:
            try:
                m = re.match(r'([0-9./]+)\s*(.+)\s*$', val)
            except TypeError:
                return
            if m:
                number, unit = Fraction(m.group(1)), m.group(2)
                wn = units.NumberWithUnit(unit, number)
                if default_unit:
                    return wn.get_number(default_unit)
                else:
                    return wn

    def run(self):
        """Generate the sound waves."""
        self.log('Loading images...')
        self.indata = []
        for path, sett in self.inputfiles:
            loaded = image.load(path)
            if isinstance(loaded[0], tuple):
                for img in loaded:
                    self.indata.append((img, sett))
            else:
                self.indata.append((loaded, sett))
        self.log('Loaded {} images.'.format(len(self.indata)))

        maxlen = max(len(x[0][1]) for x in self.indata)
        if not self.pixelduration:
            self.pixelduration = Fraction(self.fullduration, maxlen)
        elif not self.fullduration:
            self.fullduration = self.pixelduration * maxlen
        self.log('Pixel duration wants to be {} ms, full duration wants to be {} ms.'.format(
                self.pixelduration, self.fullduration))

        self.duration_ratio = self.fullduration / self.pixelduration
        self.one_pixel_samples_len = int(self.pixelduration *
                                         self.framerate / 1000)
        self.samples_len = int(self.one_pixel_samples_len * self.duration_ratio)
        self.duration_ratio = self.fullduration / self.pixelduration
        self.log('Number of samples for one pixel is {}, total number of samples is {}.'.format(
                self.one_pixel_samples_len, self.samples_len))

        self.pixelduration = Fraction(1000 * self.one_pixel_samples_len,
                                      self.framerate)
        self.fullduration = Fraction(1000 * self.samples_len, self.framerate)
        self.log('Pixel duration is {} ms, full duration is {} ms.'.format(
                self.pixelduration.numerator if self.pixelduration.denominator == 1
                else '~{:.2f}'.format(float(self.pixelduration)), 
                self.fullduration.numerator if self.fullduration.denominator == 1
                else '~{:.2f}'.format(float(self.fullduration))))

        data, settings = itertools.zip_longest(*self.indata)
        self.rgbs = tuple(x[0] for x in data)
        self.alphas = tuple(x[1] for x in data)
        self.gains = tuple(float(x['gain']) for x in settings)
        self.imgs_range = tuple(range(len(settings)))

        self.waves = {}
        self.freq_range = []
        i = 0
        for x in settings:
            row_height = len(self.alphas[i][0])
            diff = x['max'] - x['min']
            ratio = diff / row_height
            freqs = tuple(float(ratio * r + x['min']) for r in reversed(
                    range(row_height)))
            self.freq_range.append(freqs)
            for freq in freqs:
                self.waves[freq] = primitives.getlengths(freq)
            i += 1

        if self.returndata:
            return self.get_samples()
        if self.outputformat == 'wav':
            self.wavof = wave.open(self.outputfile, 'w')
            self.wavof.setnchannels(self.channels)
            self.wavof.setsampwidth(self.samplewidth // 8)
            self.wavof.setframerate(self.framerate)

        if self.play:
            pygame.mixer.init(self.framerate, -16, self.channels, 1024)
            self.sound_offset = int(self.channels * self.framerate / 5) \
                if self.playatonce else 0
            soundarr = numpy.empty(self.samples_len + self.sound_offset,
                                   dtype=numpy.int16)
            sound = pygame.sndarray.make_sound(soundarr)
            self.soundarr = pygame.sndarray.samples(sound)
            if self.playatonce:
                self.log('Starting playback...')
                sound.play()
                play_start = time.time()

        self.log('Generating sound...')
        gen_start = time.time()
        if self.showprogressbar:
            self.pbar = progressbar.ProgressBar(maxval=self.samples_len).start()
             # few have a terminal with a width above 300
            self.pbar_interval = self.samples_len // 300
        self.generate()
        if self.showprogressbar:
            self.pbar.finish()
        gen_diff = time.time() - gen_start
        self.log('Sound has been generated. The process took {:.1f} seconds.'.format(gen_diff))

        if self.play:
            if self.playatonce:
                diff = time.time() - play_start
                wait = math.ceil(self.fullduration - diff * 1000 +
                                 1000 * self.sound_offset / self.framerate)
            else:
                self.log('Starting playback...')
                sound.play()
                wait = math.ceil(self.fullduration)
            pygame.time.wait(wait)

        if self.outputformat == 'wav':
            self.wavof.close()

    def wavof_write(self, val):
        self.wavof.writeframesraw(struct.pack('<h', val))
        
    def end(self):
        """Finalize objects."""
        SoundGenerator.end(self)
        if self.play:
            pygame.mixer.quit()
