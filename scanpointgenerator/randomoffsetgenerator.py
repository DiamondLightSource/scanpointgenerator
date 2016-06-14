from collections import OrderedDict
import random

from scanpointgenerator import ScanPointGenerator


@ScanPointGenerator.register_subclass("RandomOffsetGenerator")
class RandomOffsetGenerator(ScanPointGenerator):
    """Apply a random offset to the points of an ND ScanPointGenerator"""

    def __init__(self, generator, seed, max_offset):
        """
        Args:
            generator(ScanPointGenerator): ND generator to apply offset to
            seed(int): Seed for random offset generator
            max_offset(dict): ND dict of maximum allowed offset in
            generator-defined units
        """

        self.gen = generator
        self.seed = seed
        self.RNG = random.Random(x=seed)
        self.max_offset = max_offset

        self.position_units = self.gen.position_units
        self.index_dims = self.gen.index_dims
        self.index_names = self.gen.index_names

    def get_random_number(self):
        """
        Return a random number between -1.0 and 1.0 with Gaussian distribution

        Returns:
            Float: Random number
        """
        random_number = 2.0
        while abs(random_number) > 1.0:
            random_number = self.RNG.gauss(0.0, 1.0)

        return random_number

    def apply_offset(self, point):
        """
        Apply a random offset to the Point

        Args:
            point(Point): Point to apply random offset to

        Returns:
            Point: Point with offset applied to its coordinates
        """
        for axis in point.positions.keys():
            random_number = self.get_random_number()
            point.positions[axis] += random_number * self.max_offset[axis]
        return point

    @staticmethod
    def calculate_new_upper_bound(current_point, next_point):
        """
        Calculate upper bound for current point based on next point

        Args:
            next_point(Point): Next point to calculate bound with
            current_point(Point): Current point to add bound to

        Returns:
            Point: Current point with new upper bound
        """

        for axis in current_point.positions.keys():
            current_point.upper[axis] = \
                (current_point.positions[axis] + next_point.positions[axis]) / 2
        return current_point

    @staticmethod
    def calculate_new_lower_bound(current_point, previous_point):
        """
        Calculate lower bound for current point based on previous point

        Args:
            previous_point(Point): Previous point to calculate bound with
            current_point(Point): Current point to add bound to

        Returns:
            Point: Current point with new lower bound
        """

        for axis in current_point.positions.keys():
            current_point.lower[axis] = \
                (current_point.positions[axis] + previous_point.positions[axis]) / 2
        return current_point

    def iterator(self):

        previous_point = current_point = None

        for next_point in self.gen.iterator():
            self.apply_offset(next_point)

            if previous_point is not None:
                self.calculate_new_upper_bound(current_point, next_point)
                self.calculate_new_lower_bound(current_point, previous_point)
                yield current_point
            elif current_point is not None:
                # For first point calculate upper bound and extrapolate lower bound
                self.calculate_new_upper_bound(current_point, next_point)
                for axis in current_point.positions.keys():
                    position = current_point.positions[axis]
                    upper = current_point.upper[axis]
                    current_point.lower[axis] = position - (upper - position)
                yield current_point

            previous_point = current_point
            current_point = next_point

        # For final point calculate lower bound and extrapolate upper bound
        self.calculate_new_lower_bound(current_point, previous_point)
        for axis in current_point.positions.keys():
            position = current_point.positions[axis]
            lower = current_point.lower[axis]
            current_point.upper[axis] = position + (position - lower)
        yield current_point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "RandomOffsetGenerator"
        d['generator'] = self.gen.to_dict()
        d['seed'] = self.seed
        d['max_offset'] = self.max_offset

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a RandomOffsetGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            RandomOffsetGenerator: New RandomOffsetGenerator instance
        """

        gen = ScanPointGenerator.from_dict(d['generator'])
        seed = d['seed']
        max_offset = d['max_offset']

        return cls(gen, seed, max_offset)
