from scanpointgenerator import ScanPointGenerator
from point import Point


class ArrayGenerator(ScanPointGenerator):
    """Generate a given n-dimensional array of points"""

    def __init__(self, name, units, points, lower_bounds=None, upper_bounds=None):
        """Initialise the generator

        Args:
            name (list): ND list of scannable names. E.g. ["x", "y"]
            units (str): The scannable units. E.g. "mm"
            points (list): List of ND lists of coordinates
            lower_bounds (list): List of ND lists of lower bound coordinates
            upper_bounds (list): List of ND lists of upper bound coordinates
        """

        self.name = name
        self.points = points
        self.upper_bounds = upper_bounds
        self.lower_bounds = lower_bounds
        self.num = len(points)

        self.position_units = {}
        for dimension in self.name:
            self.position_units[dimension] = units
        self.index_dims = [self.num]
        self.index_names = list(name)

    def iterator(self):

        def calculate_upper_bound():
            if i == self.num - 1:
                _lower = (coordinate + self.points[i-1][axis]) / 2
                _upper = coordinate + (coordinate - _lower)
            else:
                _upper = (self.points[i+1][axis] + coordinate) / 2
            return _upper

        def calculate_lower_bound():
            if i == 0:
                _lower = coordinate - (upper - coordinate)
            else:
                _lower = (coordinate + self.points[i-1][axis]) / 2
            return _lower

        for i in xrange(self.num):

            point = Point()
            for axis, coordinate in enumerate(self.points[i]):
                point.positions[self.name[axis]] = coordinate

                if self.upper_bounds is None:
                    upper = calculate_upper_bound()
                else:
                    upper = self.upper_bounds[i][axis]
                point.upper[self.name[axis]] = upper

                if self.lower_bounds is None:
                    lower = calculate_lower_bound()
                else:
                    lower = self.lower_bounds[i][axis]
                point.lower[self.name[axis]] = lower

            point.indexes = [i]
            yield point
