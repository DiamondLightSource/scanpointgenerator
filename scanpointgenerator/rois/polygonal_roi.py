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
from scanpointgenerator.compat import range_, np


@ROI.register_subclass("scanpointgenerator:roi/PolygonalROI:1.0")
class PolygonalROI(ROI):

    def __init__(self, points_x, points_y):
        """
        Args:
            points_x (list(double)): x positions for polygon vertices
            points_y (list(double)): y positions for polygon vertices
        """

        super(PolygonalROI, self).__init__()
        if len(points_x) != len(points_y):
            raise ValueError("Point arrays must be the same size")
        if len(points_x) < 3:
            raise ValueError("Polygon requires at least 3 vertices")
        # TODO: check points are not all collinear
        #       (i.e. describe at least a triangle)
        self.points_x = points_x
        self.points_y = points_y

    def contains_point(self, point):
        # Uses ray-casting algorithm - "fails" for complex (self-intersecting)
        # polygons, but this is intended behaviour for the moment
        # Haines 1994
        inside = False
        x = point[0]
        y = point[1]
        v1x, v1y = self.points_x[-1], self.points_y[-1]
        for v2x, v2y in zip(self.points_x, self.points_y):
            if (v1y <= y and v2y > y) or (v1y > y and v2y <= y):
                t = float(y - v1y) / float(v2y - v1y)
                if x < v1x + t * (v2x - v1x):
                    inside = not inside
            v1x, v1y = v2x, v2y
        return inside

    def mask_points(self, points):
        x = points[0]
        y = points[1]
        v1x, v1y = self.points_x[-1], self.points_y[-1]
        mask = np.full(len(x), False, dtype=np.int8)
        for v2x, v2y in zip(self.points_x, self.points_y):
            # skip horizontal edges
            if (v2y != v1y):
                vmask = np.full(len(x), False, dtype=np.int8)
                vmask |= ((y < v2y) & (y >= v1y))
                vmask |= ((y < v1y) & (y >= v2y))
                t = (y - v2y) / (v2y - v1y)
                vmask &= x < v1x + t * (v2x - v1x)
                mask ^= vmask
            v1x, v1y = v2x, v2y
        return mask

    def to_dict(self):
        d = super(PolygonalROI, self).to_dict()
        d["points_x"] = self.points_x
        d["points_y"] = self.points_y
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["points_x"], d["points_y"])
