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
    cdef double quarter_wave_len, half_wave_len, three_quarter_wave_len, wave_len
    wave_len = 1 / freq
    half_wave_len = wave_len / 2
    quarter_wave_len = half_wave_len / 2
    three_quarter_wave_len = quarter_wave_len * 3
    return (quarter_wave_len, half_wave_len, three_quarter_wave_len, wave_len)

# def getsine(double freq):
#     def _samp(double t):
#         return math.sin(t * 2 * math.pi * freq)
#     return _samp

# def gettriangle(double freq):
#     cdef double quarter_wave_len, half_wave_len, three_quarter_wave_len, wave_len
#     wave_len = 1 / freq
#     half_wave_len = wave_len / 2
#     quarter_wave_len = half_wave_len / 2
#     three_quarter_wave_len = quarter_wave_len * 3
#     def _samp(double t):
#         cdef double tr
#         tr = t % wave_len
#         if tr < quarter_wave_len:
#             return tr / quarter_wave_len
#         elif tr < half_wave_len:
#             return 1 - (tr - quarter_wave_len) / quarter_wave_len
#         elif tr < three_quarter_wave_len:
#             return -(tr - half_wave_len) / quarter_wave_len
#         else:
#             return (tr - three_quarter_wave_len) / quarter_wave_len - 1
#     return _samp

# def getsquare(double freq):
#     cdef double half_wave_len, wave_len
#     wave_len = 1 / freq
#     half_wave_len = wave_len / 2
#     def _samp(double t):
#         return 1 if t % wave_len < half_wave_len else -1
#     return _samp

# def getsawtooth(double freq):
#     cdef double half_wave_len, wave_len
#     wave_len = 1 / freq
#     half_wave_len = wave_len / 2
#     def _samp(double t):
#         cdef double tr
#         tr = t % wave_len
#         if tr < half_wave_len:
#             return tr / half_wave_len
#         else:
#             return (tr - half_wave_len) / half_wave_len - 1
#     return _samp

# cdef class PrimitiveWave:
#     def __init__(self, freq, precise=True):
#         self.frequency = freq
#         if precise:
#             self.wave_len = Fraction(1, self.frequency)
#             self.half_wave_len = Fraction(self.wave_len, 2)
#             self.quarter_wave_len = Fraction(self.half_wave_len, 2)
#             self.three_quarter_wave_len = self.quarter_wave_len * 3
#         else:
#             self.frequency = float(self.frequency)
#             self.wave_len = 1 / self.frequency
#             self.half_wave_len = self.wave_len / 2
#             self.quarter_wave_len = self.half_wave_len / 2
#             self.three_quarter_wave_len = self.quarter_wave_len * 3

# class SineWave(PrimitiveWave):
#     def __call__(self, double t):
#         return math.sin(t * 2 * math.pi * self.frequency)

# class SquareWave(PrimitiveWave):
#     def __call__(self, double t):
#         return 1 if t % self.wave_len < self.half_wave_len else -1

# class TriangleWave(PrimitiveWave):
#     def __call__(self, double t):
#         tr = t % self.wave_len
#         if tr < self.quarter_wave_len:
#             return tr / self.quarter_wave_len
#         elif tr < self.half_wave_len:
#             return 1 - (tr - self.quarter_wave_len) / self.quarter_wave_len
#         elif tr < self.three_quarter_wave_len:
#             return -(tr - self.half_wave_len) / self.quarter_wave_len
#         else:
#             return (tr - self.three_quarter_wave_len) / self.quarter_wave_len - 1

# class SawtoothWave(PrimitiveWave):
#     def __call__(self, double t):
#         cdef double tr
#         tr = t % self.wave_len
#         if tr < self.half_wave_len:
#             return tr / self.half_wave_len
#         else:
#             return (tr - self.half_wave_len) / self.half_wave_len - 1

# class SawtoothWaveReversed(SawtoothWave):
#     def __call__(self, double t):
#         return -SawtoothWave.__call__(self, t)
