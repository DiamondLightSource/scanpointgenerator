import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import StaticPointGenerator

class StaticPointGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        g = StaticPointGenerator(7)
        self.assertEqual({}, g.units)
        self.assertEqual([], g.axes)
        self.assertEqual(7, g.size)

    def test_to_dict(self):
        g = StaticPointGenerator(7)
        expected_dict = {
                "typeid":"scanpointgenerator:generator/StaticPointGenerator:1.0",
                "size": 7,
                }

        self.assertEqual(expected_dict, g.to_dict())

    def test_from_dict(self):
        d = {"size":6}
        g = StaticPointGenerator.from_dict(d)
        self.assertEqual(6, g.size)
        self.assertEqual([], g.axes)
        self.assertEqual({}, g.units)


if __name__ == "__main__":
    unittest.main(verbosity=2)
