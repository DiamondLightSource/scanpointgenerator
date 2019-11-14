###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.core import ROI
from scanpointgenerator.compat import np

with Anno("x positions for polygon vertices"):
    APointsX = Array[float]
UPointsX = Union[APointsX, Sequence[float]]
with Anno("y positions for polygon vertices"):
    APointsY = Array[float]
UPointsY = Union[APointsY, Sequence[float]]


@ROI.register_subclass("scanpointgenerator:roi/PolygonalROI:1.0")
class PolygonalROI(ROI):

    def __init__(self, points_x, points_y):
        # type: (UPointsX, UPointsY) -> None
        super(PolygonalROI, self).__init__()
        if len(points_x) != len(points_y):
            raise ValueError("Point arrays must be the same size")
        if len(points_x) < 3:
            raise ValueError("Polygon requires at least 3 vertices")
        # TODO: check points are not all collinear
        #       (i.e. describe at least a triangle)
        self.points_x = APointsX(points_x)
        self.points_y = APointsY(points_y)

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
                t = (y - v1y) / (v2y - v1y)
                vmask &= x < v1x + t * (v2x - v1x)
                mask ^= vmask
            v1x, v1y = v2x, v2y
        return mask
