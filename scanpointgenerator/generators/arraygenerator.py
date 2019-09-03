###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence, Any

from scanpointgenerator.compat import np
from scanpointgenerator.core import Generator, UAxes, UUnits, AAlternate

with Anno("The array positions"):
    APoints = Array[float]
UPoints = Union[APoints, Sequence[float]]


@Generator.register_subclass(
    "scanpointgenerator:generator/ArrayGenerator:1.0")
class ArrayGenerator(Generator):
    """Generate points from a given list of positions"""

    def __init__(self, axes=None, units=None, points=[], alternate=False,
                 **kwargs):
        # type: (UAxes, UUnits, UPoints, AAlternate, **Any) -> None

        # Check for 'axis' argument in kwargs for backwards compatibility
        assert {"axis"}.issuperset(kwargs), \
            "Unexpected argument found in kwargs %s" % list(kwargs)
        axes = kwargs.get('axis', axes)

        super(ArrayGenerator, self).__init__(
            axes, units, len(points), alternate)

        # Validation
        assert len(self.axes) == len(self.units) == 1, \
            "Expected 1D, got axes %s and units %s" % (list(self.axes),
                                                       list(self.units))

        self.points = APoints(points)

    def prepare_arrays(self, index_array):
        # Get the actual numpy array from the Array class wrapper
        points = np.array(self.points.seq)
        # add linear extension to ends of points, representing t=-1 and t=N+1
        v_left = points[0] - (points[1] - points[0])
        v_right = points[-1] + (points[-1] - points[-2])
        shape = points.shape
        shape = (shape[0] + 2,) + shape[1:]
        extended = np.empty(shape, dtype=points.dtype)
        extended[1:-1] = points
        extended[0] = v_left
        extended[-1] = v_right
        points = extended
        index_floor = np.floor(index_array).astype(np.int32)
        epsilon = index_array - index_floor
        index_floor += 1
        values = points[index_floor] + epsilon * \
                 (points[index_floor+1] - points[index_floor])
        return {self.axes[0]: values}
