import math as m

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


@Generator.register_subclass("scanpointgenerator:generator/LissajousGenerator:1.0")
class LissajousGenerator(Generator):
    """Generate the points of a Lissajous curve"""

    def __init__(self, names, units, box, num_lobes,
            num_points=None, alternate_direction=False):
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
        self.alternate_direction = alternate_direction

        if len(self.names) != len(set(self.names)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             names)

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

        self.position_units = {self.names[0]: units, self.names[1]: units}
        self.index_dims = [self.num]
        gen_name = "Lissajous"
        for axis_name in self.names[::-1]:
            gen_name = axis_name + "_" + gen_name
        self.index_names = [gen_name]

        self.axes = self.names  # For GDA

    def prepare_arrays(self, index_array):
        arrays = {}
        x0, y0 = self.centre[0], self.centre[1]
        A, B = self.x_max, self.y_max
        a, b = self.x_freq, self.y_freq
        d = self.phase_diff
        fx = lambda t: x0 + A * np.sin(a * 2*m.pi * t/self.num + d)
        fy = lambda t: y0 + B * np.sin(b * 2*m.pi * t/self.num)
        arrays[self.names[0]] = fx(index_array)
        arrays[self.names[1]] = fy(index_array)
        return arrays

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        box = dict()
        box['centre'] = self.centre
        box['width'] = self.x_max * 2
        box['height'] = self.y_max * 2

        d = dict()
        d['typeid'] = self.typeid
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
