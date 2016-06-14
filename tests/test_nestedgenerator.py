import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import NestedGenerator, LineGenerator


class NestedGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.x = LineGenerator("x", "mm", 1.0, 1.2, 3)
        self.y = LineGenerator("y", "mm", 2.0, 2.1, 2)
        self.g = NestedGenerator(self.y, self.x, alternate_direction=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(self.g.index_dims, [2, 3])
        self.assertEqual(self.g.index_names, ["y", "x"])

    def test_positions(self):
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        xlower = [0.95, 1.05, 1.15, 1.25, 1.15, 1.05]
        xupper = [1.05, 1.15, 1.25, 1.15, 1.05, 0.95]
        yindexes = [0, 0, 0, 1, 1, 1]
        xindexes = [0, 1, 2, 2, 1, 0]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(
                y=ypositions[i], x=xpositions[i]))
            self.assertEqual(p.lower, dict(
                y=ypositions[i], x=xlower[i]))
            self.assertEqual(p.upper, dict(
                y=ypositions[i], x=xupper[i]))
            self.assertEqual(p.indexes, [yindexes[i], xindexes[i]])

    def test_double_nest(self):
        self.z = LineGenerator("z", "mm", 1.0, 2.0, 2)
        self.g2 = NestedGenerator(self.z, self.g)

        zpositions = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1,
                      2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0,
                      1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        zindexes = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        yindexes = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1]
        xindexes = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0]
        for i, p in enumerate(self.g2.iterator()):
            self.assertEqual(p.positions, dict(
                z=zpositions[i], y=ypositions[i], x=xpositions[i]))
            self.assertEqual(p.indexes, [zindexes[i], yindexes[i], xindexes[i]])

if __name__ == "__main__":
    unittest.main()
