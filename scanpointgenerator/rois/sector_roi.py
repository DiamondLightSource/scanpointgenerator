###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Anno, Union, Array, Sequence

from math import hypot, atan2, pi

from scanpointgenerator.core import ROI
from scanpointgenerator.compat import np

with Anno("The centre of sector"):
    ACentre = Array[float]
UCentre = Union[ACentre, Sequence[float]]
with Anno("The radii of sector"):
    ARadii = Array[float]
URadii = Union[ARadii, Sequence[float]]
with Anno("The angles of sector"):
    AAngles = Array[float]
UAngles = Union[AAngles, Sequence[float]]


@ROI.register_subclass("scanpointgenerator:roi/SectorROI:1.0")
class SectorROI(ROI):

    def __init__(self, centre, radii, angles):
        # type: (UCentre, URadii, UAngles) -> None
        super(SectorROI, self).__init__()
        if radii[0] < 0 or radii[1] < radii[0] or radii[1] <= 0.0:
            raise ValueError("Sector size is invalid")
        self.centre = ACentre(centre)
        self.radii = ARadii(radii)
        self.angles = AAngles(self.constrain_angles(angles))

    def constrain_angles(self, angles):
        # constrain angles such that angles[0] < angles[1],
        # angles[0] in [0, 2pi), and angles[1] <= angles[0] + 2pi
        a1 = angles[0]
        a2 = angles[1]
        if a2 < a1:
            a2 += 2 * pi
            if a2 < a1:
                # input describes the full circle
                return [0, 2*pi]
        # a1 <= a2
        diff = a2 - a1
        if diff >= 2*pi:
            return [0, 2*pi]
        a1 = (a1 + 2*pi) % (2*pi)
        return [a1, a1+diff]

    def contains_point(self, point):
        angles = self.constrain_angles(self.angles)
        # get polar form (r, phi)
        x = point[0] - self.centre[0]
        y = point[1] - self.centre[1]
        r = hypot(x, y)
        phi = atan2(y, x)
        phi = (2*pi + phi) % (2*pi)

        if r < self.radii[0] or r > self.radii[1]:
            return False
        sweep = angles[1] - angles[0]
        # angle along starting at angles[0]
        theta = (phi - angles[0] + 2*pi) % (2*pi)
        return theta <= sweep

    def mask_points(self, points):
        x = points[0].copy()
        y = points[1].copy()
        x -= self.centre[0]
        y -= self.centre[1]
        r2 = (np.square(x) + np.square(y))
        phi_0, phi_1 = self.constrain_angles(self.angles)
        # phi_0 <= phi_1, phi_0 in [0, 2pi), phi_1 < 4pi
        phi_x = np.arctan2(y, x)
        # translate phi_x to range [0, 2pi]
        phi_x = (2*pi + phi_x) % (2*pi)
        # define phi_s and phi_x "offset from phi_0"
        phi_s = phi_1 - phi_0
        phi_x -= phi_0 + 2*pi
        phi_x %= 2*pi
        mask = np.full(len(x), 1, dtype=np.int8)
        mask &= r2 <= self.radii[1]
        mask &= r2 >= self.radii[0]
        mask &= (phi_x <= phi_s)
        return mask
