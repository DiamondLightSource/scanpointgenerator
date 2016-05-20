from scanpointgenerator import ScanPointGenerator
from point import Point
import math as m


class SpiralGenerator(ScanPointGenerator):

    def __init__(self, names, units, centre, radius):
        self.name = names
        self.units = units
        self.centre = centre
        self.radius = radius
        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor
        self.beta = radius / (2 * m.pi)  # Radius scale factor

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self._end_point(self.radius) - 1]
        self.index_names = names

    def _calc(self, i):
        """Calculate the coordinate for a given index"""
        theta = m.sqrt(i)
        radius = self.beta * theta
        x = self.centre[0] + radius * m.sin(theta)
        y = self.centre[1] + radius * m.cos(theta)

        return x, y

    def _end_point(self, radius):
        """Calculate the index of the final point contained by circle"""
        return int((radius / (self.alpha + self.beta)) ** 2)

    def iterator(self):
        for i in range(1, self._end_point(self.radius)):
            p = Point()
            p.positions[self.name[0]], p.positions[self.name[1]] = self._calc(i)
            p.lower[self.name[0]], p.lower[self.name[1]] = self._calc(i - 0.5)
            p.upper[self.name[0]], p.upper[self.name[1]] = self._calc(i + 0.5)
            p.indexes = [i]
            yield p
