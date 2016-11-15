from scanpointgenerator.core import ROI
from scanpointgenerator.compat import range_, np


@ROI.register_subclass("scanpointgenerator:roi/PolygonalROI:1.0")
class PolygonalROI(ROI):

    def __init__(self, points):
        super(PolygonalROI, self).__init__()
        if len(points) < 3:
            raise ValueError("Polygon requires at least 3 vertices")
        # TODO: check points are not all collinear
        #       (i.e. describe at least a triangle)
        self.points = points

    def contains_point(self, point):
        # Uses ray-casting algorithm - "fails" for complex (self-intersecting)
        # polygons, but this is intended behaviour for the moment
        # Haines 1994
        inside = False
        n = len(self.points)
        x = point[0]
        y = point[1]
        v1 = self.points[-1]
        for i in range(0, n):
            v2 = self.points[i]
            if (v1[1] <= y and v2[1] > y) or (v1[1] > y and v2[1] <= y):
                t = float(y - v1[1]) / float(v2[1] - v1[1])
                if x < v1[0] + t * (v2[0] - v1[0]):
                    inside = not inside
            v1 = v2
        return inside

    def mask_points(self, points):
        x = points[0]
        y = points[1]
        v1 = self.points[-1]
        mask = np.full(len(x), False, dtype=bool)
        for i in range_(0, len(self.points)):
            v2 = self.points[i]
            if (v2[1] == v1[1]):
                # skip horizontal edges
                v1 = v2
                continue
            vmask = ((y < v2[1]) & (y >= v1[1])) | ((y < v1[1]) & (y >= v2[1]))
            t = (y - v2[1]) / (v2[1] - v1[1])
            vmask &= x < v1[0] + t * (v2[0] - v1[0])
            mask ^= vmask
            v1 = v2
        return mask

    def to_dict(self):
        d = super(PolygonalROI, self).to_dict()
        d["points"] = self.points
        return d
    @classmethod
    def from_dict(cls, d):
        return cls(d["points"])
