import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import SquashingExcluder
from scanpointgenerator.compat import np


class TestCreateMask(ScanPointGeneratorTest):

    def setUp(self):
        self.e = SquashingExcluder(["x", "y"])

    def test_create_mask_returns_all_points(self):
        x_points = np.array([1, 2, 3, 4])
        y_points = np.array([10, 10, 20, 20])
        expected_mask = np.array([True, True, True, True])

        mask = self.e.create_mask(x_points, y_points)

        self.assertEqual(expected_mask.tolist(), mask.tolist())


class TestSerialisation(unittest.TestCase):

    def setUp(self):

        self.e = SquashingExcluder(["x", "y"])

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['typeid'] = \
            "scanpointgenerator:excluder/SquashingExcluder:1.0"
        expected_dict['axes'] = ["x", "y"]

        d = self.e.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()

        _dict['axes'] = ["x", "y"]

        e = SquashingExcluder.from_dict(_dict)

        self.assertEqual(["x", "y"], e.axes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
