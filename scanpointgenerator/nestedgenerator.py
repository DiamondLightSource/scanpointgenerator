from .scanpointgenerator import ScanPointGenerator


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
        self.position_names = outer.position_names + inner.position_names
        self.position_units = outer.position_units + inner.position_units
        self.index_dims = outer.index_dims + inner.index_dims

    def _nest(self, outer_generator, inner_generator):
        """An iterator that nests repeated runs of an inner_generator inside
        a single run of outer_generator"""
        for outer in outer_generator():
            inner_iterator = inner_generator()
            if self.snake:
                # Reverse the inner iterator as in place list
                inner_iterator = list(inner_iterator)
                inner_iterator.reverse()
            for inner in inner_iterator:
                yield outer + inner

    def positions(self):
        """An iterator yielding demand positions at each scan point"""
        return self._nest(self.outer.positions, self.inner.positions)

    def indexes(self):
        """An iterator yielding dataset indexes at each scan point"""
        return self._nest(self.outer.indexes, self.inner.indexes)

    def bounds(self):
        """An iterator yielding lower and upper position bounds for each scan
        point"""
        return self._nest(self.outer.bounds, self.inner.bounds)
