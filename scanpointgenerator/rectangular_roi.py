from scanpointgenerator.roi import ROI


@ROI.register_subclass("scanpointgenerator:roi/RectangularROI:1.0")
class RectangularROI(ROI):

    def __init__(self, start, width, height):
        super(RectangularROI, self).__init__()

        if 0.0 in [height, width]:
            raise ValueError("Rectangle must have some size")

        self.start = start
        self.width = width
        self.height = height

    def contains_point(self, point):
        x = point[0] - self.start[0]
        y = point[1] - self.start[1]
        return (x >= 0 and x < self.width) \
                and (y >= 0 and y < self.height)

    def to_dict(self):
        d = super(RectangularROI, self).to_dict()
        d['start'] = self.start
        d['width'] = self.width
        d['height'] = self.height
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d['start'], d['width'], d['height'])
