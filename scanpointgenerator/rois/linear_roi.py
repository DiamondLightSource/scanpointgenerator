from math import cos, sin

from scanpointgenerator.core import ROI


@ROI.register_subclass("scanpointgenerator:roi/LinearROI:1.0")
class LinearROI(ROI):

    def __init__(self, start, length, angle):
        super(LinearROI, self).__init__()
        if length == 0:
            raise ValueError("Line must have non-zero length")
        self.start = start
        self.length = length
        self.angle = angle

    def contains_point(self, point, epsilon=1e-15):
        # line's vector is (cphi, sphi)
        cphi = cos(self.angle)
        sphi = sin(self.angle)

        # check if it's within epsilon of end points
        x = point[0] - (self.start[0] + self.length * cphi)
        y = point[1] - (self.start[1] + self.length * sphi)
        if x * x + y * y <= epsilon * epsilon:
            return True
        x = point[0] - self.start[0]
        y = point[1] - self.start[1]
        if x * x + y * y <= epsilon * epsilon:
            return True

        # check that we're not passed the segment end points
        dp = x * cphi + y * sphi
        if dp < 0 or dp > self.length:
            return False

        # distance is scalar projection (dot product)
        # of point difference to line normal
        # normal vector of line vector is (sphi, -cphi)
        d = abs(x * sphi + y * -cphi)
        return d < epsilon

    def to_dict(self):
        d = super(LinearROI, self).to_dict()
        d["start"] = self.start
        d["length"] = self.length
        d["angle"] = self.angle
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["start"], d["length"], d["angle"])

