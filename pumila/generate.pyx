#!/usr/bin/env python3
# cython: language_level=3

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
Generates sound.
"""

import itertools
import colorsys
import math
import struct
from . import primitives

cdef double _onefour, _twofour, _threefour
_onefour, _twofour, _threefour = 1./4, 2./4, 3./4

cdef class SoundGenerator:
    """
    The actual resource-demanding sound wave generation. Only works when
    subclassed by SoundCore.
    """

    def get_samples(self):
        cdef int i, j, incr, channels, onepixsamplen
        cdef double sampnum, step, total
        channels, onepixsamplen = self.channels, self.one_pixel_samples_len
        sampnum, step = 0, 1.0 / self.framerate
        imgs_range, freq_range, gains = self.imgs_range, self.freq_range, self.gains
        rgbs, alphas = self.rgbs, self.alphas
        for imgsrgb, imgsalpha in itertools.zip_longest(
            itertools.zip_longest(*rgbs),
            itertools.zip_longest(*alphas)):
            pvars = tuple(tuple(filter(lambda x: x is not None,
                    (self.rgbafg_to_wavefunc(rgb[0], rgb[1], rgb[2], a, freq, gain)
                    for rgb, a, freq in (itertools.zip_longest(
                                    imgsrgb[j], imgsalpha[j], freq_range[j])))))
                          if imgsalpha[j] is not None else None
                          for j, gain in itertools.zip_longest(imgs_range, gains))

            for i in range(onepixsamplen):
                total, incr = 0, 0
                for pvar in pvars:
                    if pvar is None:
                        continue
                    for sampfunc in pvar:
                        total += sampfunc(sampnum)
                        incr += 1
                samp = total / incr if incr > 0 else 0
                for j in range(channels):
                    yield samp
                sampnum += step

    def rgbafg_to_wavefunc(self, int r, int g, int b, int ai,
                           double freq, double gain):
        """
        Convert rgb, alpha, frequency, and gain to a sampnum-to-sample
        function.
        """
           # transparent  # saturation == 0, if r == g == b == 0, value == 0
        if ai == 0 or     r == g == b:
            return None # pixel is either transparent or colorless, and does
                        # not matter.

        cdef double h, s, v, a
        h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
        a = ai / 255.
        cdef double amp, ar, br, l1, l2, l3, l4
        amp = float(4 * gain * s * v * a)
        if _onefour > h >= 0:
            ar, br = float(_onefour - h), float(h)
            aw, bw = primitives.sine, primitives.triangle
        elif _twofour > h >= _onefour:
            ar, br = float(_twofour - h), float(h - _onefour)
            aw, bw = primitives.triangle, primitives.square
        elif _threefour > h >= _twofour:
            ar, br = float(_threefour - h), float(h - _twofour)
            aw, bw = primitives.square, primitives.sawtooth
        else:
            ar, br = float(1 - h), float(h - _threefour)
            aw, bw = primitives.sawtooth, primitives.sine
            
        l1, l2, l3, l4 = self.waves[freq]
        def _wf(double s):
            return amp * (aw(s, freq, l1, l2, l3, l4) * ar + bw(s, freq, l1, l2, l3, l4) * br)
        return _wf

    def generate(self):
        cdef int i, j, pbar_interval
        if self.showprogressbar:
            pbar_interval, pbar_update = self.pbar_interval, self.pbar.update
        if self.outputformat == 'wav':
            wavof = self.wavof
            def wavof_write(val):
                wavof.writeframesraw(struct.pack('<h', val))
        if self.play:
            soundarr = self.soundarr
            i, j = self.sound_offset, 0
            if self.outputformat == 'wav':
                if self.showprogressbar:
                    for x in self.get_samples():
                        if j % pbar_interval == 0: pbar_update(j)
                        val = int(x * 32767)
                        soundarr[i] = val
                        wavof_write(val)
                        i += 1; j += 1
                else:
                    for x in self.get_samples():
                        val = int(x * 32767)
                        soundarr[i] = val
                        wavof_write(val)
                        i += 1; j += 1
            else:
                if self.showprogressbar:
                    for x in self.get_samples():
                        if j % pbar_interval == 0: pbar_update(j)
                        soundarr[i] = int(x * 32767)
                        i += 1; j += 1
                else:
                    for x in self.get_samples():
                        soundarr[i] = int(x * 32767)
                        i += 1; j += 1
        elif self.outputformat == 'wav':
            i = 0
            if self.showprogressbar:
                for x in self.get_samples():
                    if i % pbar_interval == 0: pbar_update(i)
                    wavof_write(int(x * 32767))
                    i += 1
            else:
                for x in self.get_samples():
                    wavof_write(int(x * 32767))
                    i += 1
        else:
            if self.showprogressbar:
                i = 0
                for x in self.get_samples():
                    if i % pbar_interval == 0: pbar_update(i)
                    i += 1
            else:
                for x in self.get_samples():
                    pass

    def end(self):
        """Finalize objects."""
        pass
