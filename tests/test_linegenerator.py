import unittest
import os
import sys

# module import
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scanpointgenerator.linegenerator import LineGenerator

class LineGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.g = LineGenerator("x", "mm", 1, 0.1, 5)

    def test_init(self):
        self.assertEqual(self.g.position_names, ["x"])
        self.assertEqual(self.g.position_units, ["mm"])
        self.assertEqual(self.g.index_dims, [5])

    def assertIteratorProduces(self, iterator, expected):
        for e in expected:
            actual = iterator.next()
            self.assertAlmostEqual(e, actual, delta=0.000001)
        self.assertRaises(StopIteration, iterator.next)

    def test_positions(self):
        expected = [1.0, 1.1, 1.2, 1.3, 1.4]
        self.assertIteratorProduces(self.g.positions(), expected)

    def test_indexes(self):
        expected = [0, 1, 2, 3, 4]
        self.assertEqual(list(self.g.indexes()), expected)

    def test_bounds(self):
        expected = [(0.95, 1.05), (1.05, 1.15), (1.15, 1.25), (1.25, 1.35),
                    (1.35, 1.45)]
        self.assertEqual(list(self.g.bounds()), expected)

if __name__=="__main__":
    unittest.main()



