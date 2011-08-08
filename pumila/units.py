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
Sound-related units.
"""

from fractions import Fraction
from . import misc
from . import info

info.add_metadata(misc.get_selfdict(__name__))

_prefixes = {k: Fraction(10)**v for k, v in {
    'y': -24,
    'z': -21,
    'a': -18,
    'f': -15,
    'p': -12,
    'n': -9,
    'μ': -6,
    'u': -6,
    'm': -3,
    'k': 3,
    'M': 6,
    'G': 9,
    'T': 12,
    'P': 15,
    'E': 18,
    'Z': 21,
    'Y': 24,
    }.items()}

class UnitError(ValueError):
    pass

class NumberWithUnit:
    def __init__(self, unit_name, number=1):
        if not unit_name:
            raise UnitError
        if len(unit_name) > 1 and unit_name[0] in _prefixes.keys():
            self.unit = unit_name[1:]
            self.base_number = number * _prefixes[unit_name[0]]
        else:
            self.unit = unit_name
            self.base_number = number
        self.number = number

    def get_number(self, unit_name=None):
        if not unit_name or unit_name == self.unit:
            return self.number
        if not unit_name.endswith(self.unit) or \
                (len(unit_name) > 1 and unit_name[0] not in _prefixes.keys()):
            raise UnitError('unit {} does not exist'.format(unit_name))
        return self.base_number / _prefixes[unit_name[0]]
