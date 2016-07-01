from collections import OrderedDict
import random

from scanpointgenerator import Mutator


class RandomOffsetMutator(Mutator):
    """Mutator to apply a random offset to the points of an ND
    ScanPointGenerator"""

    def __init__(self, seed, max_offset):
        """
        Args:
            seed(int): Seed for random offset generator
            max_offset(dict): ND dict of maximum allowed offset in
            generator-defined units
        """

        self.seed = seed
        self.RNG = random.Random(x=seed)
        self.max_offset = max_offset

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
            bool: Whether point was changed
        """
        for axis in point.positions.keys():
            if self.max_offset[axis] == 0.0:
                return False
            else:
                random_offset = self.get_random_number() * self.max_offset[axis]
                point.positions[axis] += random_offset
        return True

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

    def mutate(self, iterator):
        """
        An iterator that takes another iterator, applies a random offset to
        each point and then yields it

        Args:
            iterator: Iterator to mutate

        Yields:
            Point: Mutated points
        """

        previous_point = current_point = None
        changed = False

        for next_point in iterator:
            changed = self.apply_offset(next_point)

            if previous_point is not None:
                if changed:
                    self.calculate_new_upper_bound(current_point, next_point)
                    self.calculate_new_lower_bound(current_point, previous_point)
                yield current_point
            elif current_point is not None:
                # For first point calculate upper bound and extrapolate lower bound
                if changed:
                    self.calculate_new_upper_bound(current_point, next_point)
                    for axis in current_point.positions.keys():
                        position = current_point.positions[axis]
                        upper = current_point.upper[axis]
                        current_point.lower[axis] = position - (upper - position)
                yield current_point

            previous_point = current_point
            current_point = next_point

        # For final point calculate lower bound and extrapolate upper bound
        if changed:
            self.calculate_new_lower_bound(current_point, previous_point)
            for axis in current_point.positions.keys():
                position = current_point.positions[axis]
                lower = current_point.lower[axis]
                current_point.upper[axis] = position + (position - lower)
        yield current_point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "RandomOffsetMutator"
        d['seed'] = self.seed
        d['max_offset'] = self.max_offset

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a RandomOffsetMutator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            RandomOffsetMutator: New RandomOffsetMutator instance
        """

        seed = d['seed']
        max_offset = d['max_offset']

        return cls(seed, max_offset)
