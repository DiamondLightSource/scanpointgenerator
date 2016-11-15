import math as m

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


@Generator.register_subclass("scanpointgenerator:generator/SpiralGenerator:1.0")
class SpiralGenerator(Generator):
    """Generate the points of an Archimedean spiral"""

    def __init__(self, names, units, centre, radius, scale=1.0,
                 alternate_direction=False):
        """
        Args:
            names (list(str)): The scannable names e.g. ["x", "y"]
            units (str): The scannable units e.g. "mm"
            centre(list): List of two coordinates of centre point of spiral
            radius(float): Maximum radius of spiral
            scale(float): Gap between spiral arcs; higher scale gives
                fewer points for same radius
            alternate_direction(bool): Specifier to reverse direction if
                generator is nested
        """

        self.names = names
        self.units = units
        self.centre = centre
        self.radius = radius
        self.scale = scale
        self.alternate_direction = alternate_direction
        self.points = None
        self.points_lower = None
        self.points_upper = None

        if len(self.names) != len(set(self.names)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             names)

        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor
        self.beta = scale / (2 * m.pi)  # Radius scale factor
        self.num = self._end_point(self.radius) + 1

        self.position_units = {names[0]: units, names[1]: units}
        self.index_dims = [self._end_point(self.radius)]
        gen_name = "Spiral"
        for axis_name in self.names[::-1]:
            gen_name = axis_name + "_" + gen_name
        self.index_names = [gen_name]

        self.axes = self.names  # For GDA

    def _calc_arrays(self, offset):
        # spiral equation : r = b * phi
        # scale = 2 * pi * b
        # parameterise phi with approximation:
        # phi(t) = k * sqrt(t) (for some k)
        # number of possible t is solved by sqrt(t) = max_r / b*k
        b = self.scale / (2 * m.pi)
        k = m.sqrt(4 * m.pi) # magic scaling factor for our angle steps
        size = (self.radius) / (b * k)
        size *= size
        size = int(size) + 1 # TODO: Why the +1 ???
        phi_t = lambda t: k * np.sqrt(t + offset)
        phi = phi_t(np.arange(size))
        x = self.centre[0] + b * phi * np.sin(phi)
        y = self.centre[1] + b * phi * np.cos(phi)
        return x, y

    def produce_points(self):
        self.points = {}
        self.points_lower = {}
        self.points_upper = {}
        x = self.names[0]
        y = self.names[1]
        self.points_lower[x], self.points_lower[y] = self._calc_arrays(0)
        self.points[x], self.points[y] = self._calc_arrays(0.5)
        self.points_upper[x], self.points_upper[y] = self._calc_arrays(1.)

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
        for i in range_(0, self._end_point(self.radius) + 1):
            p = Point()
            p.indexes = [i]

            i += 0.5  # Offset so lower bound of first point is not less than 0

            p.positions[self.names[0]], p.positions[self.names[1]] = self._calc(i)
            p.upper[self.names[0]], p.upper[self.names[1]] = self._calc(i + 0.5)
            p.lower[self.names[0]], p.lower[self.names[1]] = self._calc(i - 0.5)

            yield p

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        d['names'] = self.names
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

        names = d['names']
        units = d['units']
        centre = d['centre']
        radius = d['radius']
        scale = d['scale']
        alternate_direction = d['alternate_direction']

        return cls(names, units, centre, radius, scale, alternate_direction)
