from scanpointgenerator import ScanPointGenerator
from point import Point


class LineGenerator(ScanPointGenerator):
    """Generate equally spaced scan points in one dimension"""

    def __init__(self, name, units, start, stop, num):
        """Initialise the generator

        Args:
            name (str): The scannable name. E.g. "x"
            units (str): The scannable units. E.g. "mm"
            start (float): The first position to be generated. E.g. 1.0
            stop (float): The first position to be generated. E.g. 9.0
            num (int): The number of points to generate. E.g. 5
        """

        self.name = name
        self.start = start
        self.stop = stop
        self.num = num
        self.step = abs(self.stop - self.start)/(self.num - 1)

        self.position_units = {name: units}
        self.index_dims = [self.num]
        self.index_names = [name]

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
