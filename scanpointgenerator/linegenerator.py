from collections import OrderedDict

from scanpointgenerator.compat import range_
from scanpointgenerator import Generator
from scanpointgenerator import Point


def to_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]


@Generator.register_subclass("LineGenerator")
class LineGenerator(Generator):
    """Generate a line of equally spaced N-dimensional points"""

    axis_labels = ["X", "Y", "Z"]

    def __init__(self, name, units, start, stop, num, alternate_direction=False):
        """
        Args:
            name (str): The scannable name E.g. "x" or "XYLine"
            units (str): The scannable units. E.g. "mm"
            start (float/list(float)): The first position to be generated.
                e.g. 1.0 or [1.0, 2.0]
            stop (float or list(float)): The first position to be generated.
                e.g. 5.0 or [5.0, 10.0]
            num (int): The number of points to generate. E.g. 5
            alternate_direction(bool): Specifier to reverse direction if
                generator is nested
        """

        self.name = name
        self.start = to_list(start)
        self.stop = to_list(stop)
        self.alternate_direction = alternate_direction

        if len(self.start) != len(self.stop):
            raise ValueError(
                "Dimensions of start and stop do not match")

        self.num = num
        self.num_axes = len(self.start)

        self.step = []
        if self.num < 2:
            self.step = [0]*len(self.start)
        else:
            for axis in range_(len(self.start)):
                self.step.append(
                    (self.stop[axis] - self.start[axis])/(self.num - 1))

        self.position_units = OrderedDict()
        if len(self.start) == 1:
            self.position_units[self.name] = units
            self.axes = [self.name]
        else:
            self.axes = []
            for index in range(len(self.start)):

                axis = self.name + "_"
                if index < 3:
                    axis += self.axis_labels[index]
                else:
                    axis += str(index+1)

                self.position_units[axis] = units
                self.axes.append(axis)

        self.index_dims = [self.num]
        self.index_names = [self.name]

    def _calc(self, i, axis_index):
        """Calculate the position for a given index"""
        return self.start[axis_index] + i * self.step[axis_index]

    def iterator(self):

        for i in range_(self.num):
            point = Point()

            for axis_index, axis in enumerate(self.axes):
                point.positions[axis] = self._calc(i, axis_index)
                point.lower[axis] = self._calc(i - 0.5, axis_index)
                point.upper[axis] = self._calc(i + 0.5, axis_index)

            point.indexes = [i]
            yield point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "LineGenerator"
        d['name'] = self.name
        d['units'] = list(self.position_units.values())[0]
        d['start'] = self.start
        d['stop'] = self.stop
        d['num'] = self.num
        d['alternate_direction'] = self.alternate_direction

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
        alternate_direction = d['alternate_direction']

        return cls(name, units, start, stop, num, alternate_direction)
