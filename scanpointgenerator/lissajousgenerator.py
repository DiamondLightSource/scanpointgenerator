from scanpointgenerator import ScanPointGenerator
from point import Point
import math as m


class LissajousGenerator(ScanPointGenerator):

    # Modulo of frequencies determines spacing of mesh
    # Need to adjust num_points to correspond to spacing

    def __init__(self, names, units, box, num_points, frequencies):
        self.name = names
        self.units = units

        self.x_freq = frequencies[0]
        self.y_freq = frequencies[1]
        self.x_max = box['width']/2
        self.y_max = box['height']/2
        self.centre = box['centre']

        self.phase_diff = m.pi/2  # Needs to be 0 for odd, pi/2 for even.
        self.num_points = num_points
        self.increment = 2*m.pi/num_points

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [num_points]
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
        for i in range(self.num_points):
            p = Point()
            p.positions[self.name[0]], p.positions[self.name[1]] = self._calc(i)
            p.lower[self.name[0]], p.lower[self.name[1]] = self._calc(i - 0.5)
            p.upper[self.name[0]], p.upper[self.name[1]] = self._calc(i + 0.5)
            p.indexes = [i]
            yield p
