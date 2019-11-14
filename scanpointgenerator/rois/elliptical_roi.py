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

with Anno("The centre of ellipse"):
    ACentre = Array[float]
UCentre = Union[ACentre, Sequence[float]]
with Anno("The semiaxes of ellipse"):
    ASemiaxes = Array[float]
USemiaxes = Union[ASemiaxes, Sequence[float]]
with Anno("The angle of the ellipse"):
    AAngle = float


@ROI.register_subclass("scanpointgenerator:roi/EllipticalROI:1.0")
class EllipticalROI(ROI):

    def __init__(self, centre, semiaxes, angle=0):
        # type: (UCentre, USemiaxes, AAngle) -> None
        super(EllipticalROI, self).__init__()
        if semiaxes[0] <= 0.0 or semiaxes[1] <= 0.0:
            raise ValueError("Ellipse semi-axes must be greater than zero")
        self.centre = ACentre(centre)
        self.semiaxes = ASemiaxes(semiaxes)
        self.angle = AAngle(angle)

    def contains_point(self, point):
        # transform point to the rotated ellipse frame
        x = float(point[0]) - float(self.centre[0])
        y = float(point[1]) - float(self.centre[1])
        if self.angle != 0:
            phi = -self.angle
            tx = x * cos(phi) - y * sin(phi)
            ty = x * sin(phi) + y * cos(phi)
            x = tx
            y = ty
        rx = float(self.semiaxes[0])
        ry = float(self.semiaxes[1])

        return (x * x) / (rx * rx) + (y * y) / (ry * ry) <= 1

    def mask_points(self, points):
        x = points[0].copy()
        x -= self.centre[0]
        y = points[1].copy()
        y -= self.centre[1]
        if self.angle != 0:
            phi = -self.angle
            tx = x * cos(phi) - y * sin(phi)
            ty = x * sin(phi) + y * cos(phi)
            x = tx
            y = ty
        rx2 = self.semiaxes[0] * self.semiaxes[0]
        ry2 = self.semiaxes[1] * self.semiaxes[1]
        x *= x
        x /= rx2
        y *= y
        y /= ry2
        x += y
        return x <= 1
