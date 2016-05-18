import unittest

from scanpointgenerator.gridgenerator import GridGenerator


class InitTest(unittest.TestCase):

    def setUp(self):
        bounding_box = dict(centre=[3.0, 2.0], width=6.0, height=4.0)
        inner_scan = dict(name='x', units='mm', num=3)
        outer_scan = dict(name='y', units='mm', num=2)

        self.g = GridGenerator(bounding_box, inner_scan, outer_scan, snake=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(self.g.index_dims, [2, 3])
        self.assertEqual(self.g.index_names, ["y", "x"])

    def test_positions(self):
        y_positions = [1.0, 1.0, 1.0, 3.0, 3.0, 3.0]
        x_positions = [1.0, 3.0, 5.0, 5.0, 3.0, 1.0]
        x_lower = [0.0, 2.0, 4.0, 6.0, 4.0, 2.0]
        x_upper = [2.0, 4.0, 6.0, 4.0, 2.0, 0.0]
        y_indexes = [0, 0, 0, 1, 1, 1]
        x_indexes = [0, 1, 2, 2, 1, 0]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(
                y=y_positions[i], x=x_positions[i]))
            self.assertEqual(p.lower, dict(
                y=y_positions[i], x=x_lower[i]))
            self.assertEqual(p.upper, dict(
                y=y_positions[i], x=x_upper[i]))
            self.assertEqual(p.indexes, [y_indexes[i], x_indexes[i]])
