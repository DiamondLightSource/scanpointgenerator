from collections import OrderedDict

from scanpointgenerator import Generator
from scanpointgenerator import Point


@Generator.register_subclass("ArrayGenerator")
class ArrayGenerator(Generator):
    """Generate a given n-dimensional array of points"""

    def __init__(self, name, units, points, lower_bounds=None, upper_bounds=None):
        """
        Args:
            name (str/list): ND list of scannable names e.g. "x" or ["x", "y"]
            units (str): The scannable units. E.g. "mm"
            points (list): List of ND lists of coordinates
                e.g. [1.0, 2.0, 3.0] or [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
            lower_bounds (list): List of ND lists of lower bound coordinates
            upper_bounds (list): List of ND lists of upper bound coordinates
        """

        if not isinstance(name, list):
            name = [name]
        if not isinstance(points[0], list):
            points = [[point] for point in points]
            if upper_bounds is not None:
                upper_bounds = [[point] for point in upper_bounds]
            if lower_bounds is not None:
                lower_bounds = [[point] for point in lower_bounds]

        self.name = name
        self.points = points
        self.upper_bounds = upper_bounds
        self.lower_bounds = lower_bounds

        for point in self.points:
            if len(point) != len(name):
                raise ValueError(
                    "Dimensions of name, start and stop do not match")
        if self.upper_bounds is not None:
            for point in self.upper_bounds:
                if len(point) != len(name):
                    raise ValueError(
                        "Dimensions of name, start and stop do not match")
        if self.lower_bounds is not None:
            for point in self.lower_bounds:
                if len(point) != len(name):
                    raise ValueError(
                        "Dimensions of name, start and stop do not match")

        self.num = len(points)

        self.position_units = {}
        for dimension in self.name:
            self.position_units[dimension] = units
        self.index_dims = [self.num]
        self.index_names = list(name)

    def iterator(self):

        for i in range(self.num):

            point = Point()
            for axis, coordinate in enumerate(self.points[i]):
                point.positions[self.name[axis]] = coordinate

                if self.upper_bounds is None:
                    upper = self._calculate_upper_bound(i, axis, coordinate)
                else:
                    upper = self.upper_bounds[i][axis]
                point.upper[self.name[axis]] = upper

                if self.lower_bounds is None:
                    lower = self._calculate_lower_bound(i, axis, coordinate)
                else:
                    lower = self.lower_bounds[i][axis]
                point.lower[self.name[axis]] = lower

            point.indexes = [i]
            yield point

    def _calculate_upper_bound(self, index, axis, coordinate):
        """
        Calculate upper bound for coordinate; if final coordinate then
        calculate lower bound and extrapolate upper

        Args:
            index(int): Index of coordinate in list
            axis(int): Index of coordinate axis in list
            coordinate(float): Coordinate to calculate bounds for

        Returns:
            float: Upper bound of coordinate
        """

        if index == self.num - 1:
            lower = (coordinate + self.points[index - 1][axis]) / 2
            upper = coordinate + (coordinate - lower)
        else:
            upper = (self.points[index + 1][axis] + coordinate) / 2
        return upper

    def _calculate_lower_bound(self, index, axis, coordinate):
        """
        Calculate lower bound for coordinate; if first coordinate then
        calculate upper bound and extrapolate lower

        Args:
            index(int): Index of coordinate in list
            axis(int): Index of coordinate axis in list
            coordinate(float): Coordinate to calculate bounds for

        Returns:
            float: Lower bound of coordinate
        """

        if index == 0:
            upper = (self.points[index + 1][axis] + coordinate) / 2
            lower = coordinate - (upper - coordinate)
        else:
            lower = (coordinate + self.points[index - 1][axis]) / 2
        return lower

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "ArrayGenerator"
        d['name'] = self.name
        d['units'] = list(self.position_units.values())[0]
        d['points'] = self.points
        d['lower_bounds'] = self.lower_bounds
        d['upper_bounds'] = self.upper_bounds

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a ArrayGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            ArrayGenerator: New ArrayGenerator instance
        """

        name = d['name']
        units = d['units']
        points = d['points']
        lower_bounds = d['lower_bounds']
        upper_bounds = d['upper_bounds']

        return cls(name, units, points, lower_bounds, upper_bounds)
