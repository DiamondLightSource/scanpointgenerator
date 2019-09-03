###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.core import Generator, UAxes, UUnits, ASize, AAlternate


with Anno("The first position to be generated. e.g. 1.0 or [1.0, 2.0]"):
    AStart = Array[float]
UStart = Union[AStart, Sequence[float], float]
with Anno("The final position to be generated. e.g. 5.0 or [5.0, 10.0]"):
    AStop = Array[float]
UStop = Union[AStop, Sequence[float], float]


@Generator.register_subclass(
    "scanpointgenerator:generator/LineGenerator:1.0")
class LineGenerator(Generator):
    """Generate a line of equally spaced N-dimensional points"""

    def __init__(self, axes, units, start, stop, size, alternate=False):
        # type: (UAxes, UUnits, UStart, UStop, ASize, AAlternate) -> None
        super(LineGenerator, self).__init__(axes, units, size, alternate)
        self.start = AStart(start)
        self.stop = AStop(stop)

        # Validate
        if len(self.axes) != len(self.start) or \
           len(self.axes) != len(self.stop):
            raise ValueError(
                "Dimensions of axes, start and stop do not match")

    def prepare_arrays(self, index_array):
        arrays = {}
        for axis, start, stop in zip(self.axes, self.start, self.stop):
            step = float(stop - start)
            # if self.size == 1 then single point case
            if self.size > 1:
                step /= (self.size - 1)
            else:
                # Single point, use midpoint as start. Bounds are start and stop
                start = float(start + stop) / 2.0
            arrays[axis] = index_array * step + start
        return arrays
