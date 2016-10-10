from math import cos, sin

from scanpointgenerator.core import ROI


@ROI.register_subclass("scanpointgenerator:roi/EllipticalROI:1.0")
class EllipticalROI(ROI):

    def __init__(self, centre, semiaxes, angle=0):
        super(EllipticalROI, self).__init__()
        if semiaxes[0] <= 0.0 or semiaxes[1] <= 0.0:
            raise ValueError("Ellipse semi-axes must be greater than zero")
        self.centre = centre
        self.semiaxes = semiaxes
        self.angle = angle

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

    def to_dict(self):
        d = super(EllipticalROI, self).to_dict()
        d["centre"] = self.centre
        d["semiaxes"] = self.semiaxes
        d["angle"] = self.angle
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["centre"], d["semiaxes"], d["angle"])
