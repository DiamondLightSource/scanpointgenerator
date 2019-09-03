###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from scanpointgenerator.core import ROI
import math as m

with Anno("The centre of circle"):
    ACentre = Array[float]
UCentre = Union[ACentre, Sequence[float]]
with Anno("The radius of the circle"):
    ARadius = float


@ROI.register_subclass("scanpointgenerator:roi/CircularROI:1.0")
class CircularROI(ROI):

    def __init__(self, centre, radius):
        # type: (UCentre, ARadius) -> None
        super(CircularROI, self).__init__()

        if radius <= 0.0:
            raise ValueError("Circle must have some size")

        self.radius = ARadius(radius)
        self.centre = ACentre(centre)

    def contains_point(self, point):
        if m.sqrt((point[0] - self.centre[0]) ** 2 +
                  (point[1] - self.centre[1]) ** 2) > self.radius:
            return False
        else:
            return True

    def mask_points(self, points):
        x = points[0].copy()
        x -= self.centre[0]
        y = points[1].copy()
        y -= self.centre[1]
        # use in place operations as much as possible (to save array creation)
        x *= x
        y *= y
        x += y
        r2 = self.radius * self.radius
        return x <= r2
