import unittest
from math import pi

from test_util import ScanPointGeneratorTest
from scanpointgenerator.elliptical_roi import EllipticalROI


class EllipticalROITest(unittest.TestCase):

    def test_init(self):
        roi = EllipticalROI([1.1, 2.2], [3.3, 4.4])
        self.assertEqual([1.1, 2.2], roi.centre)
        self.assertEqual([3.3, 4.4], roi.radii)

    def test_invalid_radii_fails(self):
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [-1, 1])
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [1, -1])
        with self.assertRaises(ValueError):
            roi = EllipticalROI([0, 0], [1, 0])

    def test_point_contains(self):
        roi = EllipticalROI([1, 1], [2, 1])
        p = (-1, 1)
        self.assertTrue(roi.contains_point(p))
        p = (1, 0)
        self.assertTrue(roi.contains_point(p))
        p = (3, 1)
        self.assertTrue(roi.contains_point(p))
        p = (0, 0)
        self.assertFalse(roi.contains_point(p))

    def test_to_dict(self):
        roi = EllipticalROI([1.1, 2.2], [3.3, 4.4])
        expected = {
            "typeid":"scanpointgenerator:roi/EllipticalROI:1.0",
            "centre":[1.1, 2.2],
            "radii":[3.3, 4.4]}
        self.assertEquals(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/EllipticalROI:1.0",
            "centre":[-1, 0],
            "radii":[3, 4]}
        roi = EllipticalROI.from_dict(d)
        self.assertEqual([-1, 0], roi.centre)
        self.assertEqual([3, 4], roi.radii)

if __name__ == "__main__":
    unittest.main()
