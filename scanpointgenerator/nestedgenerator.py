from scanpointgenerator import ScanPointGenerator
from point import Point

class NestedGenerator(ScanPointGenerator):
    """Nest two generators, optionally alternating each row of the inner"""

    def __init__(self, outer, inner, snake=False):
        """Initialise the generator

        Args:
            outer (ScanPointGenerator): The slower generator
            inner (ScanPointGenerator): The faster generator
            snake (bool): If True, alternate odd rows of the inner generator
        """
        self.outer = outer
        self.inner = inner
        self.snake = snake
        self.position_units = outer.position_units.copy()
        self.position_units.update(inner.position_units)
        self.index_dims = outer.index_dims + inner.index_dims

    def iterator(self):
        for i, outer in enumerate(self.outer.iterator()):
            inner_iterator = self.inner.iterator()
            alternate = False
            if self.snake and i % 2:
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
