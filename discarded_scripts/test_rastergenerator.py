import unittest

from scanpointgenerator.rastergenerator import RasterGenerator


class InitTest(unittest.TestCase):

    def setUp(self):
        bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
        inner_scan = dict(name='x', units='mm', step=2.0)
        outer_scan = dict(name='y', units='mm', step=1.0)

        self.g = RasterGenerator(bounding_box,
                                 inner_scan, outer_scan, alternate_direction=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(self.g.index_dims, [3, 3])
        self.assertEqual(self.g.index_names, ["y", "x"])

    def test_positions(self):
        positions = [{'y': 0.0, 'x': 0.0}, {'y': 0.0, 'x': 1.0},
                     {'y': 0.0, 'x': 2.0}, {'y': 0.5, 'x': 2.0},
                     {'y': 0.5, 'x': 1.0}, {'y': 0.5, 'x': 0.0},
                     {'y': 1.0, 'x': 0.0}, {'y': 1.0, 'x': 1.0},
                     {'y': 1.0, 'x': 2.0}]
        lower = [{'y': 0.0, 'x': -0.5}, {'y': 0.0, 'x': 0.5},
                 {'y': 0.0, 'x': 1.5}, {'y': 0.5, 'x': 2.5},
                 {'y': 0.5, 'x': 1.5}, {'y': 0.5, 'x': 0.5},
                 {'y': 1.0, 'x': -0.5}, {'y': 1.0, 'x': 0.5},
                 {'y': 1.0, 'x': 1.5}]
        upper = [{'y': 0.0, 'x': 0.5}, {'y': 0.0, 'x': 1.5},
                 {'y': 0.0, 'x': 2.5}, {'y': 0.5, 'x': 1.5},
                 {'y': 0.5, 'x': 0.5}, {'y': 0.5, 'x': -0.5},
                 {'y': 1.0, 'x': 0.5}, {'y': 1.0, 'x': 1.5},
                 {'y': 1.0, 'x': 2.5}]
        indexes = [[0, 0], [0, 1], [0, 2], [1, 2], [1, 1],
                   [1, 0], [2, 0], [2, 1], [2, 2]]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, positions[i])
            self.assertEqual(p.lower, lower[i])
            self.assertEqual(p.upper, upper[i])
            self.assertEqual(p.indexes, indexes[i])
