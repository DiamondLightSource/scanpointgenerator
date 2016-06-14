from collections import OrderedDict

from scanpointgenerator import ScanPointGenerator
from roi import ROI


class MaskedGenerator(object):

    def __init__(self, generator, rois):

        self.generator = generator
        self.rois = rois

    def iterator(self):

        for point in self.generator.iterator():

            contains_point = True

            for roi in self.rois:
                if not roi.contains_point(point):
                    contains_point = False
                    break

            if contains_point:
                yield point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "MaskedGenerator"
        d['generator'] = self.generator.to_dict()

        roi_list = []
        for roi in self.rois:
            roi_list.append(roi.to_dict())
        d['rois'] = roi_list

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a MaskedGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            MaskedGenerator: New MaskedGenerator instance
        """

        gen = ScanPointGenerator.from_dict(d['generator'])

        roi_list = []
        for roi_dict in d['rois']:
            roi_list.append(ROI.from_dict(roi_dict))

        return cls(gen, roi_list)
