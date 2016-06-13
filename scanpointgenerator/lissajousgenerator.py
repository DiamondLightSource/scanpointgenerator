from scanpointgenerator import ScanPointGenerator
from point import Point
import math as m


class LissajousGenerator(ScanPointGenerator):

    def __init__(self, names, units, box, num_lobes, num_points=None):
        self.name = names
        self.units = units

        num_lobes = int(num_lobes)

        self.x_freq = num_lobes
        self.y_freq = num_lobes + 1
        self.x_max = box['width']/2
        self.y_max = box['height']/2
        self.centre = box['centre']
        self.num_points = num_points

        # Phase needs to be 0 for even lobes and pi/2 for odd lobes to start
        # at centre for odd and at right edge for even
        self.phase_diff = m.pi/2 * (num_lobes % 2)
        if num_points is None:
            self.num_points = num_lobes * 100
        self.increment = 2*m.pi/self.num_points

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self.num_points]
        self.index_names = names

    def _calc(self, i):
        """Calculate the coordinate for a given index"""
        x = self.centre[0] + \
            self.x_max * m.sin(self.x_freq * i * self.increment +
                               self.phase_diff)
        y = self.centre[1] + \
            self.y_max * m.sin(self.y_freq * i * self.increment)

        return x, y

    def iterator(self):
        for i in xrange(self.num_points):
            p = Point()
            p.positions[self.name[0]], p.positions[self.name[1]] = self._calc(i)
            p.lower[self.name[0]], p.lower[self.name[1]] = self._calc(i - 0.5)
            p.upper[self.name[0]], p.upper[self.name[1]] = self._calc(i + 0.5)
            p.indexes = [i]
            yield p
