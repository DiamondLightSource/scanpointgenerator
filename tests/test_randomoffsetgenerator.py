import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.randomoffsetgenerator import RandomOffsetGenerator
from scanpointgenerator.linegenerator import LineGenerator


class RandomOffsetGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        line_gen = LineGenerator("x", "mm", 1.0, 5.0, 5)
        self.g = RandomOffsetGenerator(line_gen, 1, dict(x=0.25))

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x"])

    def test_iterator(self):
        positions = [1.0165839522345654, 1.808864087257092,
                     3.007833629207929, 4.049827994120938, 5.033343651164651]
        lower = [0.620443884723302, 1.4127240197458288,
                 2.4083488582325105, 3.5288308116644336, 4.541585822642794]
        upper = [1.4127240197458288, 2.4083488582325105,
                 3.5288308116644336, 4.541585822642794, 5.5251014796865086]
        indexes = [0, 1, 2, 3, 4]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(x=positions[i]))
            self.assertEqual(p.lower, dict(x=lower[i]))
            self.assertEqual(p.upper, dict(x=upper[i]))
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)


if __name__ == "__main__":
    unittest.main()
