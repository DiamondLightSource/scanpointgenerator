###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.core import ROI

with Anno("The point"):
    APoint = Array[float]
UPoint = Union[APoint, Sequence[float]]

@ROI.register_subclass("scanpointgenerator:roi/PointROI:1.0")
class PointROI(ROI):

    def __init__(self, point):
        # type: (UPoint) -> None
        super(PointROI, self).__init__()
        self.point = APoint(point)

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
