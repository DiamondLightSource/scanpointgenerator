import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import NestedGenerator, LineGenerator


class NestedGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.x = LineGenerator("x", "mm", 1, 0.1, 3)
        self.y = LineGenerator("y", "mm", 2, 0.1, 2)
        self.g = NestedGenerator(self.y, self.x, snake=True)

    def test_init(self):
        self.assertEqual(self.g.position_names, ["y", "x"])
        self.assertEqual(self.g.position_units, ["mm", "mm"])
        self.assertEqual(self.g.index_dims, [2, 3])

    def test_positions(self):
        expected = [[2.0, 1.0], [2.0, 1.1], [2.0, 1.2],
                    [2.1, 1.2], [2.1, 1.1], [2.1, 1.0]]
        self.assertIteratorProduces(self.g.positions(), expected)

    def test_indexes(self):
        expected = [[0, 0], [0, 1], [0, 2],
                    [1, 2], [1, 1], [1, 0]]
        self.assertIteratorProduces(self.g.indexes(), expected)

    def test_bounds(self):
        expected = [([1.95, 0.95], [2.05, 1.05]),
                    ([1.95, 1.05], [2.05, 1.15]),
                    ([1.95, 1.15], [2.05, 1.25]),
                    ([2.05, 1.15], [2.15, 1.25]),
                    ([2.05, 1.05], [2.15, 1.15]),
                    ([2.05, 0.95], [2.15, 1.05])]
        self.assertIteratorProduces(self.g.bounds(), expected)

if __name__ == "__main__":
    unittest.main()
