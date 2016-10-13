import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
from math import pi

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.rectangular_roi import RectangularROI


class InitTest(unittest.TestCase):

    def test_given_zero_height_then_error(self):

        with self.assertRaises(ValueError):
            RectangularROI([0.0, 0.0], 0.0, 5.0)

    def test_given_zero_width_then_error(self):

        with self.assertRaises(ValueError):
            RectangularROI([0.0, 0.0], 5.0, 0.0)

    def test_given_valid_params_then_set(self):

        x_start = 1.0
        y_start = 4.0
        height = 5.0
        width = 10.0
        angle = pi/4

        rectangle = RectangularROI([x_start, y_start], width, height, angle)

        self.assertEqual(rectangle.width, width)
        self.assertEqual(rectangle.height, height)
        self.assertEqual(rectangle.start[0], x_start)
        self.assertEqual(rectangle.start[1], y_start)
        self.assertEqual(rectangle.angle, angle)

    def test_default_angle(self):
        roi = RectangularROI([0, 0], 1, 1)
        self.assertEqual(0, roi.angle)


class ContainsPointTest(unittest.TestCase):

    def setUp(self):
        self.Rectangle = RectangularROI([-2.0, -2.5], 4.0, 5.0, 0)

    def test_given_valid_point_then_return_True(self):
        self.point = [1.0, 2.0]

        self.assertTrue(self.Rectangle.contains_point(self.point))

    def test_given_point_high_then_return_False(self):
        self.point = [5.0, 2.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_low_then_return_False(self):
        self.point = [-3.0, 2.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_left_then_return_False(self):
        self.point = [1.0, 4.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_right_then_return_False(self):
        self.point = [1.0, -6.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_rotated_rectangle(self):
        roi = RectangularROI([1, 2], 1, 1, pi/4)
        p = [2, 3]
        self.assertFalse(roi.contains_point(p))
        p = [2, 2]
        self.assertFalse(roi.contains_point(p))
        p = [1, 2]
        self.assertTrue(roi.contains_point(p))
        p = [1, 3.4] # (x = 1, y = sqrt(2) + 2
        self.assertTrue(roi.contains_point(p))
        p = [1.7, 2.7]
        self.assertTrue(roi.contains_point(p))
        p = [0.3, 2.705] # rounding errors cause problems on the line y = -x
        self.assertTrue(roi.contains_point(p))
        p = [1.01, 1.99]
        self.assertFalse(roi.contains_point(p))
        p = [0.99, 1.99]
        self.assertFalse(roi.contains_point(p))

class DictTest(unittest.TestCase):

    def test_to_dict(self):
        roi = RectangularROI([1, 2], 3, 4, pi/4)
        expected = {
            "typeid":"scanpointgenerator:roi/RectangularROI:1.0",
            "start":[1, 2],
            "width":3,
            "height":4,
            "angle":pi/4}
        self.assertEqual(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/RectangularROI:1.0",
            "start":[1, 2],
            "width":3,
            "height":4,
            "angle":pi/4}
        roi = RectangularROI.from_dict(d)
        self.assertEqual([1, 2], roi.start)
        self.assertEqual(3, roi.width)
        self.assertEqual(4, roi.height)
        self.assertEqual(pi/4, roi.angle)

if __name__ == "__main__":
    unittest.main()
