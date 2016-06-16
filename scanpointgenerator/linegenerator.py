from collections import OrderedDict

from generator import Generator
from point import Point


def to_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]


@Generator.register_subclass("LineGenerator")
class LineGenerator(Generator):
    """Generate equally spaced scan points in N dimensions"""

    reverse = False

    def __init__(self, name, units, start, stop, num, alternate_direction=False):
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
        self.alternate_direction = alternate_direction

        if len(self.name) != len(self.start) or \
           len(self.name) != len(self.stop):
            raise ValueError(
                "Dimensions of name, start and stop do not match")

        self.num = num
        self.num_axes = len(name)

        self.step = []
        for axis in range(len(self.start)):
            self.step.append(
                (self.stop[axis] - self.start[axis])/(self.num - 1))

        self.position_units = OrderedDict()
        for dimension in self.name:
            self.position_units[dimension] = units
        self.index_dims = [self.num]
        self.index_names = self.name

    def _calc(self, i, axis):
        """Calculate the position for a given index"""
        return self.start[axis] + i * self.step[axis]

    def iterator(self):
        if self.reverse:
            _range = reversed(xrange(self.num))
        else:
            _range = xrange(self.num)

        for i in _range:
            point = Point()

            for axis in range(self.num_axes):
                point.positions[self.name[axis]] = self._calc(i, axis)

                lower = self._calc(i - 0.5, axis)
                upper = self._calc(i + 0.5, axis)
                if self.reverse:
                    point.lower[self.name[axis]] = upper
                    point.upper[self.name[axis]] = lower
                else:
                    point.lower[self.name[axis]] = lower
                    point.upper[self.name[axis]] = upper

            point.indexes = [i]
            yield point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "LineGenerator"
        d['name'] = self.name
        d['units'] = self.position_units.values()[0]
        d['start'] = self.start
        d['stop'] = self.stop
        d['num'] = self.num

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a LineGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            LineGenerator: New LineGenerator instance
        """

        name = d['name']
        units = d['units']
        start = d['start']
        stop = d['stop']
        num = d['num']

        return cls(name, units, start, stop, num)
