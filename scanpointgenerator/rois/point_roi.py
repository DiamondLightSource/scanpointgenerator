from scanpointgenerator.core import ROI


@ROI.register_subclass("scanpointgenerator:roi/PointROI:1.0")
class PointROI(ROI):

    def __init__(self, point):
        super(PointROI, self).__init__()
        self.point = point

    def contains_point(self, point, epsilon=0):
        if epsilon == 0:
            return list(self.point) == list(point)
        x = point[0] - self.point[0]
        y = point[1] - self.point[1]
        return x * x + y * y <= epsilon * epsilon

    def mask_points(self, points, epsilon=0):
        x = points[0]
        x -= self.point[0]
        y = points[1]
        y -= self.point[1]
        x *= x
        y *= y
        x += y
        return x <= epsilon * epsilon

    def to_dict(self):
        d = super(PointROI, self).to_dict()
        d["point"] = self.point
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["point"])
