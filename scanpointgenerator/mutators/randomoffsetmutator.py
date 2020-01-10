###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import collections

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.compat import np
from scanpointgenerator.core import Mutator

with Anno("Seed for random offset generator"):
    ASeed = int
with Anno("Axes to apply random offsets to, "
          "in the order the offsets should be applied"):
    AAxes = Array[str]
UAxes = Union[AAxes, Sequence[str], str]
with Anno("Array of maximum allowed offset in generator-defined units"):
    AMaxOffset = Array[float]
UMaxOffset = Union[AMaxOffset, Sequence[float], float]


@Mutator.register_subclass("scanpointgenerator:mutator/RandomOffsetMutator:1.0")
class RandomOffsetMutator(Mutator):
    """Mutator to apply a random offset to the points of an ND
    ScanPointGenerator"""

    def __init__(self, seed, axes, max_offset):
        # type: (ASeed, UAxes, UMaxOffset) -> None

        self.seed = ASeed(seed)
        self.axes = AAxes(axes)

        # Check max_offset isn't a dict, and convert to list if it is
        if isinstance(max_offset, collections.Mapping):
            new_max_offset = []
            for axis in axes:
                new_max_offset.append(max_offset[axis])
            max_offset = new_max_offset

        self.max_offset = AMaxOffset(max_offset)

        # Validate
        if len(self.max_offset) != len(self.axes):
            raise ValueError("Dimensions of axes (%s) and max offset (%s) don't"
                             " match" % (len(self.max_offset), len(self.axes)))

    def calc_offset(self, axis, idx):
        m = self.max_offset[self.axes.index(axis)]
        x = (idx << 4) + (0 if len(axis) == 0 else ord(axis[0]))
        x ^= (self.seed << 12)
        # Apply hash algorithm to x for pseudo-randomness
        # Robert Jenkins 32 bit hash (avalanches well)
        x = (x + 0x7ED55D16) + (x << 12)
        x &= 0xFFFFFFFF # act as 32 bit unsigned before doing any right-shifts
        x = (x ^ 0xC761C23C) ^ (x >> 19)
        x = (x + 0x165667B1) + (x << 5)
        x = (x + 0xD3A2646C) ^ (x << 9)
        x = (x + 0xFD7046C5) + (x << 3)
        x &= 0xFFFFFFFF
        x = (x ^ 0xB55A4F09) ^ (x >> 16)
        x &= 0xFFFFFFFF
        if hasattr(x, "dtype"):
            r = x.astype(float)
        else:
            r = float(x)
        r /= float(0xFFFFFFFF) # r in interval [0, 1]
        r = r * 2 - 1 # r in [-1, 1]
        return m * r

    def mutate(self, point, idx):
        if hasattr(idx, "dtype"):
            # It's a numpy array:
            ''' 
            In Jython, int -> long conversion does not happen automatically within an array, therefore manually do it
            Additionally, for all but innermost dimension, lower = upper = view of positions- mutating any mutates all
            Point[s] do not explicitly preserve information about innermost dimension, so copy for all axes.
            '''
            idx = idx.astype(np.int32) - 2147483648
            point.lower = {axis: point.lower[axis].copy() for axis in point.lower}
            point.upper = {axis: point.upper[axis].copy() for axis in point.upper}
        else:
            idx = np.int32(idx) - 2147483648
        for axis in self.axes:
            point_offset = self.calc_offset(axis, idx)
            low_offset = (self.calc_offset(axis, idx-1) + point_offset) / 2
            high_offset = (self.calc_offset(axis, idx+1) + point_offset) / 2
            point.positions[axis] += point_offset
            # recalculate lower & upper bounds
            point.lower[axis] += low_offset
            point.upper[axis] += high_offset
        return point
