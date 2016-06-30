from collections import OrderedDict
import math as m

from scanpointgenerator import Generator
from scanpointgenerator import Point


@Generator.register_subclass("SpiralGenerator")
class SpiralGenerator(Generator):
    """Generate the points of an Archimedean spiral"""

    def __init__(self, names, units, centre, radius, scale=1.0, alternate_direction=False):
        """
        Args:
            names (list(str)): The scannable names e.g. ["x", "y"]
            units (str): The scannable units e.g. "mm"
            centre(list): List of two coordinates of centre point of spiral
            radius(float): Radius of spiral
            scale(float): Rate at which spiral expands; higher scale gives
                fewer points for same radius
            alternate_direction(bool): Specifier to reverse direction if
                generator is nested

        Returns:

        """
        self.name = names
        self.units = units
        self.centre = centre
        self.radius = radius
        self.scale = scale
        self.alternate_direction = alternate_direction

        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor
        self.beta = scale / (2 * m.pi)  # Radius scale factor
        self.num = self._end_point(self.radius)

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self._end_point(self.radius)]
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
        for i in range(0, self._end_point(self.radius)):
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
        d['units'] = list(self.position_units.values())[0]
        d['centre'] = self.centre
        d['radius'] = self.radius
        d['scale'] = self.scale
        d['alternate_direction'] = self.alternate_direction

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
        alternate_direction = d['alternate_direction']

        return cls(name, units, centre, radius, scale, alternate_direction)
