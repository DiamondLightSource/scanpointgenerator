from scanpointgenerator.compat import range_
from scanpointgenerator.core import Generator
from scanpointgenerator.core import Point


def to_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]


@Generator.register_subclass("scanpointgenerator:generator/LineGenerator:1.0")
class LineGenerator(Generator):
    """Generate a line of equally spaced N-dimensional points"""

    def __init__(self, name, units, start, stop, num, alternate_direction=False):
        """
        Args:
            name (str/list(str)): The scannable name(s) E.g. "x" or ["x", "y"]
            units (str): The scannable units. E.g. "mm"
            start (float/list(float)): The first position to be generated.
                e.g. 1.0 or [1.0, 2.0]
            stop (float or list(float)): The first position to be generated.
                e.g. 5.0 or [5.0, 10.0]
            num (int): The number of points to generate. E.g. 5
            alternate_direction(bool): Specifier to reverse direction if
                generator is nested
        """

        self.name = to_list(name)
        self.start = to_list(start)
        self.stop = to_list(stop)
        self.alternate_direction = alternate_direction

        if len(self.name) != len(set(self.name)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             name)

        if len(self.name) != len(self.start) or \
           len(self.name) != len(self.stop):
            raise ValueError(
                "Dimensions of name, start and stop do not match")

        self.num = num
        self.num_axes = len(self.name)

        self.step = []
        if self.num < 2:
            self.step = [0]*len(self.start)
        else:
            for axis in range_(len(self.start)):
                self.step.append(
                    (self.stop[axis] - self.start[axis])/(self.num - 1))

        self.position_units = dict()
        for dimension in self.name:
            self.position_units[dimension] = units
        self.index_dims = [self.num]

        if len(self.name) > 1:
            gen_name = "Line"
            for axis_name in self.name[::-1]:
                gen_name = axis_name + "_" + gen_name
            self.index_names = [gen_name]
        else:
            self.index_names = self.name

        self.axes = self.name  # For GDA

    def iterator(self):

        for i in range_(self.num):
            point = Point()

            for axis_index in range_(self.num_axes):
                axis_name = self.name[axis_index]
                start = self.start[axis_index]
                step = self.step[axis_index]

                point.positions[axis_name] = start + i * step
                point.lower[axis_name] = start + (i - 0.5) * step
                point.upper[axis_name] = start + (i + 0.5) * step

            point.indexes = [i]
            yield point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
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
