from scanpointgenerator import ScanPointGenerator
from point import Point


def to_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]


class LineGenerator(ScanPointGenerator):
    """Generate equally spaced scan points in N dimensions"""

    def __init__(self, name, units, start, stop, num):
        """Initialise the generator

        Args:
            name (str/list(str)): The scannable name(s) E.g. "x" or ["x", "y"]
            units (str): The scannable units. E.g. "mm"
            start (float/list(float)): The first position to be generated
            E.g. 1.0 or [1.0, 2.0]
            stop (float or list(float)): The first position to be generated. E.g. 9.0
            num (int): The number of points to generate. E.g. 5
        """

        self.name = to_list(name)
        self.start = to_list(start)
        self.stop = to_list(stop)

        if len(self.name) != len(self.start) or \
           len(self.name) != len(self.stop):
            raise ValueError(
                "Dimensions of name, start and stop do not match")

        self.num = num
        self.num_axes = len(name)

        self.step = []
        for axis in range(len(self.start)):
            self.step.append(
                abs(self.stop[axis] - self.start[axis])/(self.num - 1))

        self.position_units = {}
        for dimension in self.name:
            self.position_units[dimension] = units
        self.index_dims = [self.num]
        self.index_names = self.name

    def _calc(self, i, axis):
        """Calculate the position for a given index"""
        return self.start[axis] + i * self.step[axis]

    def iterator(self):
        for i in xrange(self.num):
            point = Point()

            for axis in range(self.num_axes):
                point.positions[self.name[axis]] = self._calc(i, axis)
                point.lower[self.name[axis]] = self._calc(i - 0.5, axis)
                point.upper[self.name[axis]] = self._calc(i + 0.5, axis)
            point.indexes = [i]
            yield point
