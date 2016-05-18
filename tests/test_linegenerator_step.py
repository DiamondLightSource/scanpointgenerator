import unittest

from scanpointgenerator.linegenerator_step import StepLineGenerator


class InitTest(unittest.TestCase):

    def setUp(self):
        self.g = StepLineGenerator("x", "mm", 0.0, 11.9, 2.0)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x"])

    def test_points(self):
        positions = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
        lower = [-1.0, 1.0, 3.0, 5.0, 7.0, 9.0]
        upper = [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]
        indexes = [0, 1, 2, 3, 4]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(x=positions[i]))
            self.assertEqual(p.lower, dict(x=lower[i]))
            self.assertEqual(p.upper, dict(x=upper[i]))
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)
