from collections import OrderedDict
import math as m

from scanpointgenerator.compat import range_
from scanpointgenerator import Generator
from scanpointgenerator import Point


@Generator.register_subclass("LissajousGenerator")
class LissajousGenerator(Generator):
    """Generate the points of a Lissajous curve"""

    def __init__(self, names, units, box, num_lobes, num_points=None):
        """
        Args:
            names (list(str)): The scannable names e.g. ["x", "y"]
            units (str): The scannable units e.g. "mm"
            box(dict): Dictionary of centre, width and height representing
                box to fill with points
            num_lobes(int): Number of x-direction lobes for curve; will
                have num_lobes+1 y-direction lobes
            num_points(int): The number of points to fill the Lissajous
                curve. Default is 250 * num_lobes
        """

        self.names = names
        self.units = units

        num_lobes = int(num_lobes)

        self.x_freq = num_lobes
        self.y_freq = num_lobes + 1
        self.x_max = box['width']/2
        self.y_max = box['height']/2
        self.centre = box['centre']
        self.num = num_points

        # Phase needs to be 0 for even lobes and pi/2 for odd lobes to start
        # at centre for odd and at right edge for even
        self.phase_diff = m.pi/2 * (num_lobes % 2)
        if num_points is None:
            self.num = num_lobes * 250
        self.increment = 2*m.pi/self.num

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self.num]
        gen_name = "Lissajous"
        for axis_name in self.names[::-1]:
            gen_name = axis_name + "_" + gen_name
        self.index_names = [gen_name]

        self.axes = self.names  # For GDA

    def _calc(self, i):
        """Calculate the coordinate for a given index"""
        x = self.centre[0] + \
            self.x_max * m.sin(self.x_freq * i * self.increment +
                               self.phase_diff)
        y = self.centre[1] + \
            self.y_max * m.sin(self.y_freq * i * self.increment)

        return x, y

    def iterator(self):
        for i in range_(self.num):
            p = Point()
            p.positions[self.names[0]], p.positions[self.names[1]] = self._calc(i)
            p.lower[self.names[0]], p.lower[self.names[1]] = self._calc(i - 0.5)
            p.upper[self.names[0]], p.upper[self.names[1]] = self._calc(i + 0.5)
            p.indexes = [i]
            yield p

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        box = OrderedDict()
        box['centre'] = self.centre
        box['width'] = self.x_max * 2
        box['height'] = self.y_max * 2

        d = OrderedDict()
        d['type'] = "LissajousGenerator"
        d['names'] = self.names
        d['units'] = list(self.position_units.values())[0]
        d['box'] = box
        d['num_lobes'] = self.x_freq
        d['num_points'] = self.num

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

        names = d['names']
        units = d['units']
        box = d['box']
        num_lobes = d['num_lobes']
        num_points = d['num_points']

        return cls(names, units, box, num_lobes, num_points)
