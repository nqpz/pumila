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
Primitive waves.
"""

import math
from fractions import Fraction

cdef double _pi2
_pi2 = 2.0 * math.pi

cpdef double sine(double t, double freq, double quarter_wave_len,
                  double half_wave_len, double three_quarter_wave_len,
                  double wave_len):
    return math.sin(t * _pi2 * freq)

cpdef double triangle(double t, double freq, double quarter_wave_len,
                  double half_wave_len, double three_quarter_wave_len,
                  double wave_len):
    cdef double tr
    tr = t % wave_len
    if tr < quarter_wave_len:
        return tr / quarter_wave_len
    elif tr < half_wave_len:
        return 1 - (tr - quarter_wave_len) / quarter_wave_len
    elif tr < three_quarter_wave_len:
        return -(tr - half_wave_len) / quarter_wave_len
    else:
        return (tr - three_quarter_wave_len) / quarter_wave_len - 1

cpdef double square(double t, double freq, double quarter_wave_len,
                  double half_wave_len, double three_quarter_wave_len,
                  double wave_len):
    return 1 if t % wave_len < half_wave_len else -1

cpdef double sawtooth(double t, double freq, double quarter_wave_len,
                  double half_wave_len, double three_quarter_wave_len,
                  double wave_len):
    cdef double tr
    tr = t % wave_len
    if tr < half_wave_len:
        return tr / half_wave_len
    else:
        return (tr - half_wave_len) / half_wave_len - 1

def getlengths(double freq):
    """Get wave length * 1/4, * 1/2, * 3/4, and * 1 for a frequency."""
    cdef double quarter_wave_len, half_wave_len, three_quarter_wave_len, wave_len
    wave_len = 1 / freq
    half_wave_len = wave_len / 2
    quarter_wave_len = half_wave_len / 2
    three_quarter_wave_len = quarter_wave_len * 3
    return (quarter_wave_len, half_wave_len, three_quarter_wave_len, wave_len)
