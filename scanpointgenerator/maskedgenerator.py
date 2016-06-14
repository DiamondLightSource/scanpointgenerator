

class MaskedGenerator(object):

    def __init__(self, generator, roi):

        self.generator = generator
        self.roi = roi

    def iterator(self):

        for point in self.generator.iterator():
            if self.roi.contains_point(point):
                yield point
