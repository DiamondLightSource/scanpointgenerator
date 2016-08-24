from scanpointgenerator.roi import ROI


@ROI.register_subclass("scanpointgenerator:roi/RectangularROI:1.0")
class RectangularROI(ROI):

    def __init__(self, centre, width, height):
        super(RectangularROI, self).__init__(centre)

        if 0.0 in [height, width]:
            raise ValueError("Rectangle must have some size")

        self.width = width
        self.height = height

    def contains_point(self, point):

        if abs(point[0] - self.centre[0]) > self.width/2:
            return False
        elif abs(point[1] - self.centre[1]) > self.height/2:
            return False
        else:
            return True

    def to_dict(self):
        d = super(RectangularROI, self).to_dict()
        d['width'] = self.width
        d['height'] = self.height
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d['centre'], d['width'], d['height'])
