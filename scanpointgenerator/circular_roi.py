from roi import BaseROI
import math as m


class CircularROI(BaseROI):

    def __init__(self, centre, radius):
        super(CircularROI, self).__init__("Circle", centre)

        if radius == 0.0:
            raise ValueError("Circle must have some size")

        self.radius = radius

    def contains_point(self, point):
        if m.sqrt((point.positions['x'] - self.centre[0]) ** 2 +
                  (point.positions['y'] - self.centre[1]) ** 2) > self.radius:
            return False
        else:
            return True
