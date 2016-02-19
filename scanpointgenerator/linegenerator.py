from .scanpointgenerator import ScanPointGenerator


class LineGenerator(ScanPointGenerator):
    """Generate equally spaced scan points in one dimension"""

    def __init__(self, name, units, start, step, num):
        """Initialise the generator.

        Args:
            name (str): The scannable name. E.g. "x"
            units (str): The scannable units. E.g. "mm"
            start (float): The first position to be generated. E.g. 1.5
            step (float): The increment for each successive position. E.g. 0.5
            num (int): The number of points to generate. E.g. 5
        """
        self.start = start
        self.step = step
        self.num = num
        self.position_names = [name]
        self.position_units = [units]
        self.index_dims = [self.num]

    def _calc(self, i):
        """Calculate the position for a given index"""
        return self.start + i * self.step

    def positions(self):
        """An iterator yielding demand positions at each scan point"""
        for i in xrange(self.num):
            yield self._calc(i)

    def indexes(self):
        """An iterator yielding dataset indexes at each scan point"""
        return xrange(self.num)

    def bounds(self):
        """An iterator yielding lower and upper position bounds for each scan
        point"""
        for i in xrange(self.num):
            lower = self._calc(i - 0.5)
            upper = self._calc(i + 0.5)
            yield (lower, upper)
