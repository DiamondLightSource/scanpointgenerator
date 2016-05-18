import unittest

from scanpointgenerator.rastergenerator import RasterGenerator


class InitTest(unittest.TestCase):

    def setUp(self):
        bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
        inner_scan = dict(name='x', units='mm', step=2.0)
        outer_scan = dict(name='y', units='mm', step=1.0)

        self.g = RasterGenerator(bounding_box, inner_scan, outer_scan, snake=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(self.g.index_dims, [3, 3])
        self.assertEqual(self.g.index_names, ["y", "x"])

    def test_positions(self):
        y_positions = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
        x_positions = [0.0, 2.0, 4.0, 4.0, 2.0, 0.0, 0.0, 2.0, 4.0]
        x_lower = [-1.0, 1.0, 3.0, 5.0, 3.0, 1.0, -1.0, 1.0, 3.0]
        x_upper = [1.0, 3.0, 5.0, 3.0, 1.0, -1.0, 1.0, 3.0, 5.0]
        y_indexes = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        x_indexes = [0, 1, 2, 2, 1, 0, 0, 1, 2]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(
                y=y_positions[i], x=x_positions[i]))
            self.assertEqual(p.lower, dict(
                y=y_positions[i], x=x_lower[i]))
            self.assertEqual(p.upper, dict(
                y=y_positions[i], x=x_upper[i]))
            self.assertEqual(p.indexes, [y_indexes[i], x_indexes[i]])
