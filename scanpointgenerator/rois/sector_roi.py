from scanpointgenerator.core import ROI
from math import hypot, atan2, pi


@ROI.register_subclass("scanpointgenerator:roi/SectorROI:1.0")
class SectorROI(ROI):

    def __init__(self, centre, radii, angles):
        super(SectorROI, self).__init__()
        if radii[0] < 0 or radii[1] < radii[0] or radii[1] <= 0.0:
            raise ValueError("Sector size is invalid")
        self.centre = centre
        self.radii = radii
        self.angles = self.constrain_angles(angles)

    def constrain_angles(self, angles):
        # sort out tricky angles (i.e. make sure angle[0] < angle[1])
        a1 = angles[0]
        a2 = angles[1]
        if a2 < a1:
            a2 += 2 * pi
            if a2 < a1:
                # input describes the full circle
                a1 = 0
                a2 = 2 * pi
        return [a1, a2]

    def contains_point(self, point):
        angles = self.constrain_angles(self.angles)
        # get polar form (r, phi)
        x = point[0] - self.centre[0]
        y = point[1] - self.centre[1]
        r = hypot(x, y)
        phi = atan2(y, x)
        if phi < 0:
            phi += 2 * pi

        # Easy checks first
        if r < self.radii[0] or r > self.radii[1]:
            return False
        if phi >= self.angles[0] and phi < self.angles[1]:
            return True

        sweep = angles[1] - angles[0]
        if sweep >= 2 * pi:
            return True
        if phi < angles[0]:
            phi += 2 * pi
        return phi <= angles[0] + sweep

    def to_dict(self):
        d = super(SectorROI, self).to_dict()
        d["centre"] = self.centre
        d["radii"] = self.radii
        d["angles"] = self.angles
        return d

    @classmethod
    def from_dict(cls, d):
        centre = d['centre']
        radii = d['radii']
        angles = d['angles']
        return cls(centre, radii, angles)
