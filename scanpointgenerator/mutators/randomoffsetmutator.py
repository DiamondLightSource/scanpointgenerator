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
        r = float(x) / float(0xFFFFFFFF) # r in interval [0, 1]
        r = r * 2 - 1 # r in [-1, 1]
        return m * r

    def mutate(self, point, idx):
        point_offset = None
        for axis in self.axes:
            offset = self.calc_offset(axis, idx)
            point.positions[axis] += offset
            if axis in point.lower and axis in point.upper:
                inner_axis = axis
                point_offset = offset
        if inner_axis is not None:
            # recalculate lower bounds
            idx -= 1
            prev_offset = self.calc_offset(inner_axis, idx)
            offset = (point_offset + prev_offset) / 2
            point.lower[inner_axis] += offset
            # recalculate upper bounds
            idx += 2
            next_offset = self.calc_offset(inner_axis, idx)
            offset = (point_offset + next_offset) / 2
            point.upper[inner_axis] += offset
        return point
