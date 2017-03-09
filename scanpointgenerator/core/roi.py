###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

class ROI(object):

    _roi_lookup = {}
    typeid="scanpointgenerator:roi/ROI:1.0"

    def __init__(self):
        pass

    def contains_point(self, point):
        raise NotImplementedError

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        return d

    @classmethod
    def from_dict(cls, d):
        """
        Abstract method to create a ROI instance from a
        serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            ROI: New ROI instance
        """

        roi_type = d["typeid"]
        roi = cls._roi_lookup[roi_type]
        assert roi is not cls, \
            "Subclass %s did not redefine from_dict" % roi_type
        r = roi.from_dict(d)
        return r

    @classmethod
    def register_subclass(cls, roi_type):
        """
        Register a subclass so from_dict() works

        Args:
            roi_type (ROI): Subclass to register
        """

        def decorator(roi):

            roi.typeid = roi_type
            cls._roi_lookup[roi_type] = roi

            return roi
        return decorator
