###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from math import cos, sin

from scanpointgenerator.core import ROI
from scanpointgenerator.compat import np


@ROI.register_subclass("scanpointgenerator:roi/LinearROI:1.0")
class LinearROI(ROI):

    def __init__(self, start, length, angle):
        super(LinearROI, self).__init__()
        if length == 0:
            raise ValueError("Line must have non-zero length")
        self.start = start
        self.length = length
        self.angle = angle

    def contains_point(self, point, epsilon=1e-15):
        # line's vector is (cphi, sphi)
        cphi = cos(self.angle)
        sphi = sin(self.angle)

        # check if it's within epsilon of end points
        x = point[0] - (self.start[0] + self.length * cphi)
        y = point[1] - (self.start[1] + self.length * sphi)
        if x * x + y * y <= epsilon * epsilon:
            return True
        x = point[0] - self.start[0]
        y = point[1] - self.start[1]
        if x * x + y * y <= epsilon * epsilon:
            return True

        # check that we're not passed the segment end points
        dp = x * cphi + y * sphi
        if dp < 0 or dp > self.length:
            return False

        # distance is scalar projection (dot product)
        # of point difference to line normal
        # normal vector of line vector is (sphi, -cphi)
        d = abs(x * sphi + y * -cphi)
        return d < epsilon

    def mask_points(self, points, epsilon=1e-15):
        cphi = cos(self.angle)
        sphi = sin(self.angle)
        x = points[0] - self.start[0]
        y = points[1] - self.start[1]

        # test for being past segment end-points
        dp = x * cphi + y * sphi
        mask = np.full(len(x), True, dtype=np.int8)
        mask &= dp >= 0
        mask &= dp <= self.length

        # distance is scalar projection (dot-product) of
        # point difference to line normal (normal = (sphi, -cphi))
        dp = np.abs(x * sphi + y * -cphi)
        mask &= dp < epsilon

        # include all points in an epsilon circle around endpoints
        x *= x
        y *= y
        mask |= x + y <= epsilon * epsilon
        x = points[0] - (self.start[0] + self.length * cphi)
        y = points[1] - (self.start[1] + self.length * sphi)
        x *= x
        y *= y
        mask |= x + y <= epsilon * epsilon
        return mask

    def to_dict(self):
        d = super(LinearROI, self).to_dict()
        d["start"] = self.start
        d["length"] = self.length
        d["angle"] = self.angle
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["start"], d["length"], d["angle"])

