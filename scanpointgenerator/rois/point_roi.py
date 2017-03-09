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

from scanpointgenerator.core import ROI


@ROI.register_subclass("scanpointgenerator:roi/PointROI:1.0")
class PointROI(ROI):

    def __init__(self, point):
        super(PointROI, self).__init__()
        self.point = point

    def contains_point(self, point, epsilon=0):
        if epsilon == 0:
            return list(self.point) == list(point)
        x = point[0] - self.point[0]
        y = point[1] - self.point[1]
        return x * x + y * y <= epsilon * epsilon

    def mask_points(self, points, epsilon=0):
        x = points[0].copy()
        x -= self.point[0]
        y = points[1].copy()
        y -= self.point[1]
        x *= x
        y *= y
        x += y
        return x <= epsilon * epsilon

    def to_dict(self):
        d = super(PointROI, self).to_dict()
        d["point"] = self.point
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["point"])
