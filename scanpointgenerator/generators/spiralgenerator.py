import math as m

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


@Generator.register_subclass("scanpointgenerator:generator/SpiralGenerator:1.0")
class SpiralGenerator(Generator):
    """Generate the points of an Archimedean spiral"""

    def __init__(self, axes, units, centre, radius, scale=1.0,
                 alternate=False):
        """
        Args:
            axes (list(str)): The scannable axes e.g. ["x", "y"]
            units (list(str)): The scannable units e.g. ["mm", "mm"]
            centre(list): List of two coordinates of centre point of spiral
            radius(float): Maximum radius of spiral
            scale(float): Gap between spiral arcs; higher scale gives
                fewer points for same radius
            alternate(bool): Specifier to reverse direction if
                generator is nested
        """

        self.axes = axes
        self.centre = centre
        self.radius = radius
        self.scale = scale
        self.alternate = alternate
        self.units = {d:u for d,u in zip(axes, units)}

        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             axes)

        gen_name = "Spiral"
        for axis_name in self.axes[::-1]:
            gen_name = axis_name + "_" + gen_name
        self.index_names = [gen_name]

        # spiral equation : r = b * phi
        # scale = 2 * pi * b
        # parameterise phi with approximation:
        # phi(t) = k * sqrt(t) (for some k)
        # number of possible t is solved by sqrt(t) = max_r / b*k
        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor = k
        self.beta = scale / (2 * m.pi)  # Radius scale factor = b
        self.size = int((self.radius / (self.alpha * self.beta)) ** 2) + 1

    def prepare_arrays(self, index_array):
        arrays = {}
        b = self.beta
        k = self.alpha
        size = self.size
        # parameterise phi with approximation:
        # phi(t) = k * sqrt(t) (for some k)
        phi_t = lambda t: k * np.sqrt(t + 0.5)
        phi = phi_t(index_array)
        x = self.centre[0] + b * phi * np.sin(phi)
        y = self.centre[1] + b * phi * np.cos(phi)
        arrays[self.axes[0]] = x
        arrays[self.axes[1]] = y
        return arrays

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        d['axes'] = self.axes
        d['units'] = [self.units[a] for a in self.axes]
        d['centre'] = self.centre
        d['radius'] = self.radius
        d['scale'] = self.scale
        d['alternate'] = self.alternate

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

        axes = d['axes']
        units = d['units']
        centre = d['centre']
        radius = d['radius']
        scale = d['scale']
        alternate = d['alternate']

        return cls(axes, units, centre, radius, scale, alternate)
