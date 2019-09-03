###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from math import cos, sin

from scanpointgenerator.core import ROI
from scanpointgenerator.compat import np

with Anno("The start point of the rectangle"):
    AStart = Array[float]
UStart = Union[AStart, Sequence[float]]
with Anno("The width of the rectangle"):
    AWidth = float
with Anno("The height of the rectangle"):
    AHeight = float
with Anno("The angle of the rectangle"):
    AAngle = float


@ROI.register_subclass("scanpointgenerator:roi/RectangularROI:1.0")
class RectangularROI(ROI):

    def __init__(self, start, width, height, angle=0):
        # type: (UStart, AWidth, AHeight, AAngle) -> None
        super(RectangularROI, self).__init__()

        if 0.0 in [height, width]:
            raise ValueError("Rectangle must have some size")

        self.start = AStart(start)
        self.width = AWidth(width)
        self.height = AHeight(height)
        self.angle = AAngle(angle)

    def contains_point(self, point):
        # transform point to the rotated rectangle frame
        x = point[0] - self.start[0]
        y = point[1] - self.start[1]
        if self.angle != 0:
            phi = -self.angle
            rx = x * cos(phi) - y * sin(phi)
            ry = x * sin(phi) + y * cos(phi)
            x = rx
            y = ry
        return (x >= 0 and x <= self.width) \
                and (y >= 0 and y <= self.height)

    def mask_points(self, points):
        x = points[0].copy()
        x -= self.start[0]
        y = points[1].copy()
        y -= self.start[1]
        if self.angle != 0:
            phi = -self.angle
            rx = x * cos(phi) - y * sin(phi)
            ry = x * sin(phi) + y * cos(phi)
            x = rx
            y = ry
        mask_x = np.logical_and(x >= 0, x <= self.width)
        mask_y = np.logical_and(y >= 0, y <= self.height)
        return np.logical_and(mask_x, mask_y)
