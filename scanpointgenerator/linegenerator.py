from scanpointgenerator import ScanPointGenerator
from point import Point


class LineGenerator(ScanPointGenerator):
    """Generate equally spaced scan points in one dimension"""

    def __init__(self, name, units, start, step, num):
        """Args:
            name (str): The scannable name. E.g. "x"
            units (str): The scannable units. E.g. "mm"
            start (float): The first position to be generated. E.g. 1.5
            step (float): The increment for each successive position. E.g. 0.5
            num (int): The number of points to generate. E.g. 5
        """
        self.name = name
        self.start = start
        self.step = step
        self.num = num
        self.position_units = {name: units}
        self.index_dims = [self.num]

    def _calc(self, i):
        """Calculate the position for a given index"""
        return self.start + i * self.step

    def iterator(self):
        for i in xrange(self.num):
            point = Point()
            point.positions[self.name] = self._calc(i)
            point.lower[self.name] = self._calc(i - 0.5)
            point.upper[self.name] = self._calc(i + 0.5)
            point.indexes = [i]
            yield point
