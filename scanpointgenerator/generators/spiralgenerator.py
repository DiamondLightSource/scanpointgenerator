###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import math as m

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.compat import np
from scanpointgenerator.core import Generator, UAxes, UUnits, AAlternate

with Anno("The centre of the lissajous curve"):
    ACentre = Array[float]
UCentre = Union[ACentre, Sequence[float]]
with Anno("Maximum radius of spiral"):
    ARadius = float
with Anno("Gap between spiral arcs; "
          "higher scale gives fewer points for same radius"):
    AScale = float


@Generator.register_subclass("scanpointgenerator:generator/SpiralGenerator:1.0")
class SpiralGenerator(Generator):
    """Generate the points of an Archimedean spiral"""

    def __init__(self, axes, units, centre, radius, scale=1.0, alternate=False):
        # type: (UAxes, UUnits, UCentre, ARadius, AScale, AAlternate) -> None

        self.centre = ACentre(centre)
        self.radius = ARadius(radius)
        self.scale = AScale(scale)

        # Validate
        assert len(self.centre) == len(axes) == 2, \
            "Expected centre %s and axes %s to be 2 dimensional" % (
                list(self.centre), list(axes))

        # spiral equation : r = b * phi
        # scale = 2 * pi * b
        # parameterise phi with approximation:
        # phi(t) = k * sqrt(t) (for some k)
        # number of possible t is solved by sqrt(t) = max_r / b*k
        self.alpha = m.sqrt(4 * m.pi)  # Theta scale factor = k
        self.beta = scale / (2 * m.pi)  # Radius scale factor = b
        size = int((self.radius / (self.alpha * self.beta)) ** 2) + 1
        super(SpiralGenerator, self).__init__(axes, units, size, alternate)

    def prepare_arrays(self, index_array):
        # parameterise phi with approximation:
        # phi(t) = k * sqrt(t) (for some k)
        phi = self.alpha * np.sqrt(index_array + 0.5)
        arrays = {
          self.axes[0]: self.centre[0] + self.beta * phi * np.sin(phi),
          self.axes[1]: self.centre[1] + self.beta * phi * np.cos(phi)
        }
        return arrays
