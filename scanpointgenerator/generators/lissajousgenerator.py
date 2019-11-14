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
from scanpointgenerator.core import Generator, UAxes, UUnits, ASize, AAlternate

with Anno("The centre of the lissajous curve"):
    ACentre = Array[float]
UCentre = Union[ACentre, Sequence[float]]
with Anno("The [height, width] of the curve"):
    ASpan = Array[float]
USpan = Union[ASpan, Sequence[float]]
with Anno("Number of x-direction lobes for curve; "
          "will have lobes+1 y-direction lobes"):
    ALobes = int


@Generator.register_subclass(
    "scanpointgenerator:generator/LissajousGenerator:1.0")
class LissajousGenerator(Generator):
    """Generate the points of a Lissajous curve"""

    def __init__(self, axes, units, centre, span, lobes, size=None, alternate=False):
        # type: (UAxes, UUnits, UCentre, USpan, ALobes, ASize, AAlternate) -> None
        # Default for size is 250 * lobes if not specified
        self.centre = ACentre(centre)
        self.span = ASpan(span)
        self.lobes = ALobes(lobes)
        if size is None:
            size = self.lobes * 250

        # Validate
        assert len(self.centre) == len(self.span) == len(axes) == 2, \
            "Expected centre %s, span %s and axes %s to be 2 dimensional" % (
                list(self.centre), list(self.span), list(axes))

        # Phase needs to be 0 for even lobes and pi/2 for odd lobes to start
        # at centre for odd and at right edge for even
        self.x_freq = self.lobes
        self.y_freq = self.lobes + 1
        self.x_max, self.y_max = self.span[0]/2, self.span[1]/2
        self.phase_diff = m.pi/2 * (self.lobes % 2)
        self.increment = 2*m.pi/size
        super(LissajousGenerator, self).__init__(axes, units, size, alternate)

    def prepare_arrays(self, index_array):
        arrays = {
          self.axes[0]: self.centre[0] +
                        self.x_max *
                        np.sin(
                            self.x_freq *
                            self.increment *
                            index_array +
                            self.phase_diff
                        ),
          self.axes[1]: self.centre[1] +
                        self.y_max *
                        np.sin(
                            self.y_freq *
                            self.increment *
                            index_array
                        )
        }
        return arrays
