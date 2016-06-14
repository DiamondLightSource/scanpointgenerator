from collections import OrderedDict
import math as m

from scanpointgenerator import ScanPointGenerator
from point import Point


@ScanPointGenerator.register_subclass("SpiralGenerator")
class SpiralGenerator(ScanPointGenerator):

    def __init__(self, names, units, centre, radius, scale=1.0):
        self.name = names
        self.units = units
        self.centre = centre
        self.radius = radius
        self.scale = scale

        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor
        self.beta = scale / (2 * m.pi)  # Radius scale factor

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self._end_point(self.radius) - 1]
        self.index_names = names

    def _calc(self, i):
        """Calculate the coordinate for a given index"""
        theta = self.alpha * m.sqrt(i)
        radius = self.beta * theta
        x = self.centre[0] + radius * m.sin(theta)
        y = self.centre[1] + radius * m.cos(theta)

        return x, y

    def _end_point(self, radius):
        """Calculate the index of the final point contained by circle"""
        return int((radius / (self.alpha * self.beta)) ** 2)

    def iterator(self):
        for i in xrange(0, self._end_point(self.radius)):
            p = Point()
            p.indexes = [i]

            i += 0.5  # Offset so lower bound of first point is not less than 0

            p.positions[self.name[0]], p.positions[self.name[1]] = self._calc(i)
            p.upper[self.name[0]], p.upper[self.name[1]] = self._calc(i + 0.5)
            p.lower[self.name[0]], p.lower[self.name[1]] = self._calc(i - 0.5)

            yield p

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "SpiralGenerator"
        d['name'] = self.name
        d['units'] = self.position_units.values()[0]
        d['centre'] = self.centre
        d['radius'] = self.radius
        d['scale'] = self.scale

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a SpiralGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            SpiralGenerator: New SpiralGenerator instance
        """

        name = d['name']
        units = d['units']
        centre = d['centre']
        radius = d['radius']
        scale = d['scale']

        return cls(name, units, centre, radius, scale)
