import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
from math import pi

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.elliptical_roi import EllipticalROI


class EllipticalROITest(unittest.TestCase):

    def test_init(self):
        roi = EllipticalROI([1.1, 2.2], [3.3, 4.4], pi/4)
        self.assertEqual([1.1, 2.2], roi.centre)
        self.assertEqual([3.3, 4.4], roi.semiaxes)
        self.assertEqual(pi/4, roi.angle)

    def test_default_angle(self):
        roi = EllipticalROI([1.1, 2.2], [3.3, 4.4])
        self.assertEqual([1.1, 2.2], roi.centre)
        self.assertEqual([3.3, 4.4], roi.semiaxes)
        self.assertEqual(0, roi.angle)

    def test_invalid_semiaxes_fails(self):
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [-1, 1])
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [1, -1])
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [1, 0])

    def test_point_contains(self):
        roi = EllipticalROI([1, 1], [2, 1], 0)
        p = (-1, 1)
        self.assertTrue(roi.contains_point(p))
        p = (1, 0)
        self.assertTrue(roi.contains_point(p))
        p = (3, 1)
        self.assertTrue(roi.contains_point(p))
        p = (0, 0)
        self.assertFalse(roi.contains_point(p))

    def test_rotated_point_contains(self):
        r = EllipticalROI([1, 2], [2, 1], 0)
        p = (1, 3)
        self.assertTrue(r.contains_point(p))
        roi = EllipticalROI([1, 2], [2, 1], pi/6)
        p = (3, 1)
        self.assertFalse(roi.contains_point(p))
        p = (1, 0)
        self.assertFalse(roi.contains_point(p))
        p = (2.73, 3)
        self.assertTrue(roi.contains_point(p))
        p = (3, 4.27)
        self.assertFalse(roi.contains_point(p))
        p = (-0.73, 1)
        self.assertTrue(roi.contains_point(p))

    def test_to_dict(self):
        roi = EllipticalROI([1.1, 2.2], [3.3, 4.4], pi/4)
        expected = {
            "typeid":"scanpointgenerator:roi/EllipticalROI:1.0",
            "centre":[1.1, 2.2],
            "semiaxes":[3.3, 4.4],
            "angle":pi/4}
        self.assertEquals(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/EllipticalROI:1.0",
            "centre":[-1, 0],
            "semiaxes":[3, 4],
            "angle":pi/4}
        roi = EllipticalROI.from_dict(d)
        self.assertEqual([-1, 0], roi.centre)
        self.assertEqual([3, 4], roi.semiaxes)
        self.assertEqual(pi/4, roi.angle)

if __name__ == "__main__":
    unittest.main()
