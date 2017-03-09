###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator


def to_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]


@Generator.register_subclass("scanpointgenerator:generator/LineGenerator:1.0")
class LineGenerator(Generator):
    """Generate a line of equally spaced N-dimensional points"""

    def __init__(self, axes, units, start, stop, size, alternate=False):
        """
        Args:
            axes (str/list(str)): The scannable axes E.g. "x" or ["x", "y"]
            units (str/list(str)): The scannable units. E.g. "mm" or ["mm", "mm"]
            start (float/list(float)): The first position to be generated.
                e.g. 1.0 or [1.0, 2.0]
            stop (float or list(float)): The final position to be generated.
                e.g. 5.0 or [5.0, 10.0]
            size (int): The number of points to generate. E.g. 5
            alternate(bool): Specifier to reverse direction if
                generator is nested
        """

        self.axes = to_list(axes)
        self.start = to_list(start)
        self.stop = to_list(stop)
        self.alternate = alternate
        self.units = {d:u for (d, u) in zip(self.axes, to_list(units))}

        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             axes)

        if len(self.axes) != len(self.start) or \
           len(self.axes) != len(self.stop):
            raise ValueError(
                "Dimensions of axes, start and stop do not match")

        self.size = size

        self.step = []
        if self.size < 2:
            self.step = [0]*len(self.start)
        else:
            for axis in range_(len(self.start)):
                self.step.append(
                    (self.stop[axis] - self.start[axis])/(self.size - 1))

    def prepare_arrays(self, index_array):
        arrays = {}
        for axis, start, stop in zip(self.axes, self.start, self.stop):
            d = stop - start
            step = float(d)
            # if self.size == 1 then single point case
            if self.size > 1:
                step /= (self.size - 1)
            f = lambda t: (t * step) + start
            arrays[axis] = f(index_array)
        return arrays

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        d['axes'] = self.axes
        d['units'] = [self.units[a] for a in self.axes]
        d['start'] = self.start
        d['stop'] = self.stop
        d['size'] = self.size
        d['alternate'] = self.alternate

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a LineGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            LineGenerator: New LineGenerator instance
        """

        axes = d['axes']
        units = d['units']
        start = d['start']
        stop = d['stop']
        size = d['size']
        alternate = d['alternate']

        return cls(axes, units, start, stop, size, alternate)
