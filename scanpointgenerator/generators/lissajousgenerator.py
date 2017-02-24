import math as m

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


@Generator.register_subclass("scanpointgenerator:generator/LissajousGenerator:1.0")
class LissajousGenerator(Generator):
    """Generate the points of a Lissajous curve"""

    def __init__(self, axes, units, box, num_lobes,
            num_points=None, alternate=False):
        """
        Args:
            axes (list(str)): The scannable axes e.g. ["x", "y"]
            units (list(str)): The scannable units e.g. ["mm", "mm"]
            box(dict): Dictionary of centre, width and height representing
                box to fill with points
            num_lobes(int): Number of x-direction lobes for curve; will
                have num_lobes+1 y-direction lobes
            num_points(int): The number of points to fill the Lissajous
                curve. Default is 250 * num_lobes
        """

        self.axes = axes
        self.units = {d:u for d,u in zip(axes, units)}
        self.alternate = alternate

        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             axes)

        num_lobes = int(num_lobes)

        self.x_freq = num_lobes
        self.y_freq = num_lobes + 1
        self.x_max = box['width']/2
        self.y_max = box['height']/2
        self.centre = box['centre']
        self.size = num_points

        # Phase needs to be 0 for even lobes and pi/2 for odd lobes to start
        # at centre for odd and at right edge for even
        self.phase_diff = m.pi/2 * (num_lobes % 2)
        if num_points is None:
            self.size = num_lobes * 250
        self.increment = 2*m.pi/self.size

        self.index_dims = [self.size]
        gen_name = "Lissajous"
        for axis_name in self.axes[::-1]:
            gen_name = axis_name + "_" + gen_name
        self.index_names = [gen_name]

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

        box = dict()
        box['centre'] = self.centre
        box['width'] = self.x_max * 2
        box['height'] = self.y_max * 2

        d = dict()
        d['typeid'] = self.typeid
        d['axes'] = self.axes
        d['units'] = [self.units[a] for a in self.axes]
        d['box'] = box
        d['num_lobes'] = self.x_freq
        d['num_points'] = self.size

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
        box = d['box']
        num_lobes = d['num_lobes']
        num_points = d['num_points']

        return cls(axes, units, box, num_lobes, num_points)
