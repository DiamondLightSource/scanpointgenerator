###
# Copyright (c) 2019 Diamond Light Source Ltd.
#
# Contributors:
#    Matt Taylor - Initial implementation
#
###

from scanpointgenerator.core import Excluder, UExcluderAxes
from scanpointgenerator.compat import np


@Excluder.register_subclass("scanpointgenerator:excluder/SquashingExcluder:1.0")
class SquashingExcluder(Excluder):

    """A class that allows every point through. Used to squash generators"""

    def __init__(self, axes):
        # type: (UExcluderAxes) -> None
        super(SquashingExcluder, self).__init__(axes)

    def create_mask(self, *point_arrays):
        """Create a boolean array specifying the points to exclude.

        All points are included, none are excluded for this excluder.

        Args:
            *point_arrays (numpy.array(float)): Array of points for each axis

        Returns:
            np.array(int8): Array of points to exclude

        """
        length = len(point_arrays[0])
        for arr in point_arrays:
            if len(arr) != length:
                raise ValueError("Points lengths must be equal")

        mask = np.ones_like(point_arrays[0], dtype=np.int8)

        return mask
