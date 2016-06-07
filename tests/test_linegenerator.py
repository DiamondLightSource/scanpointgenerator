import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LineGenerator


class LineGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = LineGenerator("x", "mm", 1.0, 9.0, 5)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x"])

    def test_iterator(self):
        positions = [1.0, 3.0, 5.0, 7.0, 9.0]
        lower = [0.0, 2.0, 4.0, 6.0, 8.0]
        upper = [2.0, 4.0, 6.0, 8.0, 10.0]
        indexes = [0, 1, 2, 3, 4]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(x=positions[i]))
            self.assertEqual(p.lower, dict(x=lower[i]))
            self.assertEqual(p.upper, dict(x=upper[i]))
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)

if __name__ == "__main__":
    unittest.main()



