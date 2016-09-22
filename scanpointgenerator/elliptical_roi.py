from scanpointgenerator.roi import ROI


@ROI.register_subclass("scanpointgenerator:roi/EllipticalROI:1.0")
class EllipticalROI(ROI):

    def __init__(self, centre, radii):
        super(EllipticalROI, self).__init__()
        if radii[0] <= 0.0 or radii[1] <= 0.0:
            raise ValueError("Ellipse radii must be greater than zero")
        self.centre = centre
        self.radii = radii

    def contains_point(self, point):
        x = float(point[0]) - float(self.centre[0])
        y = float(point[1]) - float(self.centre[1])
        rx = float(self.radii[0])
        ry = float(self.radii[1])
        return (x * x) / (rx * rx) + (y * y) / (ry * ry) <= 1

    def to_dict(self):
        d = super(EllipticalROI, self).to_dict()
        d["centre"] = self.centre
        d["radii"] = self.radii
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["centre"], d["radii"])
