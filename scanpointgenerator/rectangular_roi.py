from scanpointgenerator.roi import ROI


class RectangularROI(ROI):

    def __init__(self, centre, width, height):
        super(RectangularROI, self).__init__("Rectangle", centre)

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
