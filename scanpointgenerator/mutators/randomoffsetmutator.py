from scanpointgenerator.core import Mutator
from scanpointgenerator.core import random


@Mutator.register_subclass("scanpointgenerator:mutator/RandomOffsetMutator:1.0")
class RandomOffsetMutator(Mutator):
    """Mutator to apply a random offset to the points of an ND
    ScanPointGenerator"""

    def __init__(self, seed, axes, max_offset):
        """
        Args:
            seed(int): Seed for random offset generator
            axes(list): Axes to apply random offsets to, in the order the
            offsets should be applied
            max_offset(dict): ND dict of maximum allowed offset in
            generator-defined units
        """

        self.seed = seed
        self.axes = axes
        self.max_offset = max_offset

    def mutate(self, point):
        seed = self.seed
        for idx in point.indexes:
            seed = (seed << 4) ^ idx
        for axis in sorted(self.axes):
            m = self.max_offset[axis]
            r = random.Random(seed).random()
            point.positions[axis] += m * r
            seed += 1
        return point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid
        d['seed'] = self.seed
        d['axes'] = self.axes
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
        axes = d['axes']
        max_offset = d['max_offset']

        return cls(seed, axes, max_offset)
