

class BaseROI(object):

    def __init__(self, name, centre):

        self.name = name
        self.centre = centre

    def contains_point(self, point):
        raise NotImplementedError
