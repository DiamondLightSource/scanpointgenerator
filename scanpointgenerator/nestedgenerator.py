from collections import OrderedDict

from scanpointgenerator import ScanPointGenerator
from point import Point


@ScanPointGenerator.register_subclass("NestedGenerator")
class NestedGenerator(ScanPointGenerator):
    """Nest two generators, optionally alternating each row of the inner"""

    def __init__(self, outer, inner, alternate_direction=False):
        """Initialise the generator

        Args:
            outer (ScanPointGenerator): The slower generator
            inner (ScanPointGenerator): The faster generator
            alternate_direction (bool): If True, alternate odd rows of the inner generator
        """
        self.outer = outer
        self.inner = inner
        self.alternate_direction = alternate_direction

        self.position_units = outer.position_units.copy()
        self.position_units.update(inner.position_units)
        self.index_dims = outer.index_dims + inner.index_dims
        self.index_names = outer.index_names + inner.index_names

    def iterator(self):
        for i, outer in enumerate(self.outer.iterator()):
            inner_iterator = self.inner.iterator()
            alternate = False
            if self.alternate_direction and i % 2:
                alternate = True
                # Reverse the inner iterator as in place list
                inner_iterator = list(inner_iterator)
                inner_iterator.reverse()
            for inner in inner_iterator:
                point = Point()
                # Insert outer points
                point.positions.update(outer.positions)
                point.lower.update(outer.positions)
                point.upper.update(outer.positions)
                # Insert inner points
                point.positions.update(inner.positions)
                # alternate has lower and upper bound swapped
                if alternate:
                    point.upper.update(inner.lower)
                    point.lower.update(inner.upper)
                else:
                    point.upper.update(inner.upper)
                    point.lower.update(inner.lower)
                # Insert indexes
                point.indexes = outer.indexes + inner.indexes
                yield point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "NestedGenerator"
        d['outer'] = self.outer.to_dict()
        d['inner'] = self.inner.to_dict()
        d['alternate_direction'] = self.alternate_direction

        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a NestedGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            NestedGenerator: New NestedGenerator instance
        """

        outer = ScanPointGenerator.from_dict(d['outer'])
        inner = ScanPointGenerator.from_dict(d['inner'])
        alternate_direction = d['alternate_direction']

        return cls(outer, inner, alternate_direction)
