from roi import ROI
import math as m


class CircularROI(ROI):

    def __init__(self, centre, radius):
        super(CircularROI, self).__init__("Circle", centre)

        if radius == 0.0:
            raise ValueError("Circle must have some size")

        self.radius = radius

    def contains_point(self, point):
        if m.sqrt((point[0] - self.centre[0]) ** 2 +
                  (point[1] - self.centre[1]) ** 2) > self.radius:
            return False
        else:
            return True

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = super(CircularROI, self).to_dict()
        d['type'] = "CircularROI"
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

        name = d['name']
        centre = d['centre']
        radius = d['radius']

        return cls(name, centre, radius)
