###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import math as m

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


@Generator.register_subclass("scanpointgenerator:generator/LissajousGenerator:1.0")
class LissajousGenerator(Generator):
    """Generate the points of a Lissajous curve"""

    def __init__(self, axes, units, centre, span, lobes, size=None, alternate=False):
        """
        Args:
            axes (list(str)): The scannable axes e.g. ["x", "y"]
            units (list(str)): The scannable units e.g. ["mm", "mm"]
            centre (list(float)): The centre of the lissajous curve
            span (list(float)): The [height, width] of the curve
            num(int): Number of x-direction lobes for curve; will
                have lobes+1 y-direction lobes
            size(int): The number of points to fill the Lissajous
                curve. Default is 250 * lobes
        """

        self.axes = axes
        self.units = {d:u for d,u in zip(axes, units)}
        self.alternate = alternate

        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             axes)

        lobes = int(lobes)

        self.x_freq = lobes
        self.y_freq = lobes + 1
        self.x_max, self.y_max = span[0]/2, span[1]/2
        self.centre = centre
        self.size = size

        # Phase needs to be 0 for even lobes and pi/2 for odd lobes to start
        # at centre for odd and at right edge for even
        self.phase_diff = m.pi/2 * (lobes % 2)
        if size is None:
            self.size = lobes * 250
        self.increment = 2*m.pi/self.size

    def prepare_arrays(self, index_array):
        arrays = {}
        x0, y0 = self.centre[0], self.centre[1]
        A, B = self.x_max, self.y_max
        a, b = self.x_freq, self.y_freq
        d = self.phase_diff
        fx = lambda t: x0 + A * np.sin(a * 2*m.pi * t/self.size + d)
        fy = lambda t: y0 + B * np.sin(b * 2*m.pi * t/self.size)
        arrays[self.axes[0]] = fx(index_array)
        arrays[self.axes[1]] = fy(index_array)
        return arrays

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        d['axes'] = self.axes
        d['units'] = [self.units[a] for a in self.axes]
        d['centre'] = self.centre
        d['span'] = [self.x_max * 2, self.y_max * 2]
        d['lobes'] = self.x_freq
        d['size'] = self.size

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a LissajousGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            LissajousGenerator: New LissajousGenerator instance
        """

        axes = d['axes']
        units = d['units']
        centre = d['centre']
        span = d['span']
        lobes = d['lobes']
        size = d['size']

        return cls(axes, units, centre, span, lobes, size)
