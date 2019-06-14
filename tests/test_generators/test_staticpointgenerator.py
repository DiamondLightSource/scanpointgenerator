import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import StaticPointGenerator

class StaticPointGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        g = StaticPointGenerator(7)
        self.assertEqual([], g.units)
        self.assertEqual([], g.axes)
        self.assertEqual(7, g.size)

    def test_array_positions(self):
        g = StaticPointGenerator(5)

        g.prepare_positions()
        g.prepare_bounds()

        self.assertEqual({}, g.positions)
        self.assertEqual({}, g.bounds)

    def test_array_positions_with_axis(self):
        g = StaticPointGenerator(5, 'repeats')
        positions = [1, 2, 3, 4, 5]
        bounds = [1, 2, 3, 4, 5, 6]

        g.prepare_positions()
        g.prepare_bounds()

        self.assertEqual(positions, g.positions['repeats'].tolist())
        self.assertEqual(bounds, g.bounds['repeats'].tolist())

    def test_to_dict(self):
        g = StaticPointGenerator(7)
        expected_dict = {
                "typeid":"scanpointgenerator:generator/StaticPointGenerator:1.0",
                "size": 7,
                "axes": [],
                }

        self.assertEqual(expected_dict, g.to_dict())

    def test_to_dict_with_axis(self):
        g = StaticPointGenerator(7, 'repeats')
        expected_dict = {
                "typeid":"scanpointgenerator:generator/StaticPointGenerator:1.0",
                "size": 7,
                "axes": ['repeats'],
                }

        self.assertEqual(expected_dict, g.to_dict())

    def test_from_dict(self):
        d = {"size":6}
        g = StaticPointGenerator.from_dict(d)
        self.assertEqual(6, g.size)
        self.assertEqual([], g.axes)
        self.assertEqual([], g.units)


if __name__ == "__main__":
    unittest.main(verbosity=2)
