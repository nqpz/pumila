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
Loads images.
"""

import sys
import os.path
import tempfile
import zipfile
import re
import pygame
import numpy

def load(path):
    """Load image from path."""
    if path.endswith('.ora'):
        return load_ora(path)
    try:
        surf = pygame.image.load(path)
        try:
            rgb = pygame.surfarray.pixels3d(surf)
        except pygame.error:
            rgb = pygame.surfarray.array3d(surf)
        try:
            alpha = pygame.surfarray.pixels_alpha(surf)
        except (ValueError, pygame.error):
            alpha = numpy.empty((len(rgb), len(rgb[0])), dtype=numpy.uint8)
            alpha[:] = 255
        return (rgb, alpha)
    except pygame.error:
        raise ValueError('file {} is not loadable'.format(repr(path)))

def load_ora(path):
    """Load OpenRaster image from path."""

    temp_path = tempfile.mkdtemp()
    zf = zipfile.ZipFile(path)
    zf.extractall(temp_path)

    with open(os.path.join(temp_path, 'stack.xml')) as f:
        xml = f.read()
        
    files = sorted(filter(lambda x: not x.endswith('background.png'),
                          ('{}/{}'.format(temp_path, x.strip('"\''))
                           for x in re.findall(r'src=(.+?.png)', xml))))
    return tuple(map(load, files))
