import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.circular_roi import CircularROI


class InitTest(unittest.TestCase):

    def test_given_zero_radius_then_error(self):

        with self.assertRaises(ValueError):
            CircularROI([0.0, 0.0], 0.0)

    def test_given_valid_params_then_set(self):

        x_centre = 1.0
        y_centre = 4.0
        radius = 5.0

        circle = CircularROI([x_centre, y_centre], radius)

        self.assertEqual(circle.radius, radius)
        self.assertEqual(circle.centre[0], x_centre)
        self.assertEqual(circle.centre[1], y_centre)


class ContainsPointTest(unittest.TestCase):

    def setUp(self):
        self.Circle = CircularROI([5.0, 15.0], 5.0)

        self.point = [7.0, 11.0]

    def test_given_valid_point_then_return_True(self):
        self.assertTrue(self.Circle.contains_point(self.point))

    def test_given_point_outside_then_return_False(self):
        self.point = [9.0, 11.0]

        self.assertFalse(self.Circle.contains_point(self.point))

class DictTest(unittest.TestCase):

    def test_to_dict(self):
        roi = CircularROI([1.1, 2.2], 3.3)
        expected = {
            "typeid":"scanpointgenerator:roi/CircularROI:1.0",
            "centre":[1.1, 2.2],
            "radius":3.3}
        self.assertEquals(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/CircularROI:1.0",
            "centre":[0, 0.1],
            "radius":1}
        roi = CircularROI.from_dict(d)
        self.assertEqual([0, 0.1], roi.centre)
        self.assertEqual(1, roi.radius)

if __name__ == "__main__":
    unittest.main()
