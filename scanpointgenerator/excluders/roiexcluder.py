###
# Copyright (c) 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence, deserialize_object

from scanpointgenerator.core import Excluder, UExcluderAxes, ROI
from scanpointgenerator.compat import np

with Anno("List of regions of interest"):
    ARois = Array[ROI]
URois = Union[ARois, Sequence[ROI]]


@Excluder.register_subclass("scanpointgenerator:excluder/ROIExcluder:1.0")
class ROIExcluder(Excluder):

    """A class to exclude points outside of regions of interest."""

    def __init__(self, rois, axes):
        # type: (URois, UExcluderAxes) -> None
        super(ROIExcluder, self).__init__(axes)
        self.rois = ARois([deserialize_object(r, ROI) for r in rois])

    def create_mask(self, *point_arrays):
        """Create a boolean array specifying the points to exclude.

        The resulting mask is created from the union of all ROIs.

        Args:
            *point_arrays (numpy.array(float)): Array of points for each axis

        Returns:
            np.array(int8): Array of points to exclude

        """
        l = len(point_arrays[0])
        for arr in point_arrays:
            if len(arr) != l:
                raise ValueError("Points lengths must be equal")

        mask = np.zeros_like(point_arrays[0], dtype=np.int8)
        for roi in self.rois:
            # Accumulate all True entries
            # Points outside of all ROIs will be excluded
            mask |= roi.mask_points(point_arrays)

        return mask
