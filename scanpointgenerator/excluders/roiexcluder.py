from scanpointgenerator.core import Excluder, ROI
from scanpointgenerator.compat import np


@Excluder.register_subclass("scanpointgenerator:excluder/ROIExcluder:1.0")
class ROIExcluder(Excluder):

    """A class to exclude points outside of regions of interest."""

    def __init__(self, rois, axes):
        """
        Args:
            rois(list(ROI)): List of regions of interest
            axes(list(str)): Names of axes to exclude points from

        """
        super(ROIExcluder, self).__init__(axes)

        self.rois = rois

    def create_mask(self, x_points, y_points):
        """Create a boolean array specifying the points to exclude.

        The resulting mask is created from the union of all ROIs.

        Args:
            x_points(numpy.array(float)): Array of points for x-axis
            y_points(numpy.array(float)): Array of points for y-axis

        Returns:
            np.array: Boolean array of points to exclude

        """
        if len(x_points) != len(y_points):
            raise ValueError("Points lengths must be equal")

        mask = np.zeros_like(x_points, dtype=bool)
        for roi in self.rois:
            # Accumulate all True entries
            # Points outside of all ROIs will be excluded
            mask |= roi.mask_points([x_points, y_points])

        return mask

    def to_dict(self):
        """Construct dictionary from attributes."""
        d = super(ROIExcluder, self).to_dict()
        d['typeid'] = self.typeid
        d['rois'] = [roi.to_dict() for roi in self.rois]

        return d

    @classmethod
    def from_dict(cls, d):
        """Create a ROIExcluder from a serialised dictionary.

        Args:
            d(dict): Dictionary of attributes

        Returns:
            ROIExcluder: New instance of ROIExcluder

        """
        rois = [ROI.from_dict(roi_dict) for roi_dict in d['rois']]
        axes = d['axes']

        return cls(rois, axes)
