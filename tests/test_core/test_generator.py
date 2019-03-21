import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import Generator

from pkg_resources import require
require("mock")
from mock import MagicMock


class ScanPointGeneratorBaseTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = Generator(["x", "y"], ["mm", "cm"], 1)

    def test_init(self):
        self.assertEqual(dict(x="mm", y="cm"), self.g.axis_units())
        self.assertEqual(["x", "y"], self.g.axes)
        self.assertEqual(1, self.g.size)
        self.assertEqual(False, self.g.alternate)

    def test_prepare_positions_raises(self):
        with self.assertRaises(NotImplementedError):
            self.g.prepare_positions()

    def test_prepare_bounds_raises(self):
        with self.assertRaises(NotImplementedError):
            self.g.prepare_bounds()

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['axes'] = ["x", "y"]
        expected_dict['units'] = ["mm", "cm"]
        expected_dict['size'] = 1
        expected_dict['alternate'] = False

        self.assertEqual(expected_dict, self.g.to_dict())


if __name__ == "__main__":
    unittest.main()
