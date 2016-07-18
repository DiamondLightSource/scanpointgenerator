from collections import OrderedDict

from scanpointgenerator import Mutator
from scanpointgenerator import random


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
        self.RNG = random.Random(seed)
        self.max_offset = max_offset

    def get_random_number(self):
        """
        Return a random number between -1.0 and 1.0 with Gaussian distribution

        Returns:
            Float: Random number
        """
        random_number = 2.0
        while abs(random_number) > 1.0:
            random_number = self.RNG.random()

        return random_number

    def apply_offset(self, point):
        """
        Apply a random offset to the Point

        Args:
            point(Point): Point to apply random offset to

        Returns:
            bool: Whether point was changed
        """

        changed = False
        for axis in point.positions.keys():
            if self.max_offset[axis] == 0.0:
                pass
            else:
                random_offset = self.get_random_number() * self.max_offset[axis]
                point.positions[axis] += random_offset
                changed = True
                
        return changed

    @staticmethod
    def calculate_new_bounds(current_point, next_point):
        """
        Take two adjacent points and recalculate their shared bound

        Args:
            next_point(Point): Next point
            current_point(Point): Current point
        """

        for axis in current_point.positions.keys():
            new_bound = (current_point.positions[axis] +
                         next_point.positions[axis]) / 2

            current_point.upper[axis] = new_bound
            next_point.lower[axis] = new_bound

    def mutate(self, iterator):
        """
        An iterator that takes another iterator, applies a random offset to
        each point and then yields it

        Args:
            iterator: Iterator to mutate

        Yields:
            Point: Mutated points
        """

        next_point = current_point = None

        for next_point in iterator:
            changed = self.apply_offset(next_point)

            if current_point is not None:
                if changed:
                    # If point wasn't changed don't update bounds
                    if next_point.lower == current_point.upper:
                        # If leaving and re-entering ROI don't update bounds
                        self.calculate_new_bounds(current_point, next_point)

                yield current_point

            current_point = next_point

        yield next_point

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
