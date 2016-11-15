from scanpointgenerator.core import ROI
import math as m


@ROI.register_subclass("scanpointgenerator:roi/CircularROI:1.0")
class CircularROI(ROI):

    def __init__(self, centre, radius):
        super(CircularROI, self).__init__()

        if radius == 0.0:
            raise ValueError("Circle must have some size")

        self.radius = radius
        self.centre = centre

    def contains_point(self, point):
        if m.sqrt((point[0] - self.centre[0]) ** 2 +
                  (point[1] - self.centre[1]) ** 2) > self.radius:
            return False
        else:
            return True

    def mask_points(self, points):
        x = points[0]
        x -= self.centre[0]
        y = points[1]
        y -= self.centre[1]
        # use in place operations as much as possible (to save array creation)
        x *= x
        y *= y
        x += y
        r2 = self.radius * self.radius
        return x <= r2

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = super(CircularROI, self).to_dict()
        d['centre'] = self.centre
        d['radius'] = self.radius

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a CircularROI instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            CircularROI: New CircularROI instance
        """

        centre = d['centre']
        radius = d['radius']

        return cls(centre, radius)
