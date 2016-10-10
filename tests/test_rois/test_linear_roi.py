import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
from math import pi, sqrt

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.linear_roi import LinearROI

class LinearROIInitTest(unittest.TestCase):

    def test_init(self):
        l = LinearROI([0, 1], 2, 3)
        self.assertEquals([0, 1], l.start)
        self.assertEquals(2, l.length)
        self.assertEquals(3, l.angle)

    def test_invalid_length_raises(self):
        with self.assertRaises(ValueError):
            l = LinearROI([0, 0], 0, 0)

class LinearROIContainsTest(unittest.TestCase):

    def test_default_epsilon(self):
        l = LinearROI([0, 0], 1, 0)
        p = [0, 1e-16]
        self.assertNotEqual([0, 0], p)
        self.assertTrue(l.contains_point(p))
        p = [0, 2e-15]
        self.assertFalse(l.contains_point(p))

    def test_near_endpoints(self):
        l = LinearROI([1, 1], 1.4, pi/4)
        p = [0.9, 0.9]
        self.assertFalse(l.contains_point(p, 0))
        self.assertTrue(l.contains_point(p, 0.2))
        p = [2, 2]
        self.assertFalse(l.contains_point(p, 0))
        self.assertTrue(l.contains_point(p, 0.02))

        l = LinearROI([0, 0], sqrt(2), pi/4)
        p = [1, 1]
        self.assertTrue(l.contains_point(p))

    def test_near_midsection(self):
        l = LinearROI([-1, -1], 3 * sqrt(2), pi/4)
        p = [0, 0]
        self.assertTrue(l.contains_point(p))
        p = [0, 0.1]
        self.assertFalse(l.contains_point(p))

    def test_wide_angle(self):
        l = LinearROI([0, 0], sqrt(2), 5 * pi/4)
        p = [-1, -1]
        self.assertTrue(l.contains_point(p))
        p = [-1.0001, -1.0001]
        self.assertFalse(l.contains_point(p))
        p = [-0.1, -0.001]
        self.assertFalse(l.contains_point(p))

    def test_negative_length(self):
        l = LinearROI([0, 0], -sqrt(2), pi/4)
        p = [-1, -1]
        self.assertTrue(l.contains_point(p))
        p = [-1.0001, -1.0001]
        self.assertFalse(l.contains_point(p))
        p = [-0.1, -0.001]
        self.assertFalse(l.contains_point(p))

    def test_negative_angle(self):
        l = LinearROI([0, 0], sqrt(2), -pi/4)
        p = [0, 0]
        self.assertTrue(l.contains_point(p))
        p = [1, -1]
        self.assertTrue(l.contains_point(p))
        p = [0.1, 0.1]
        self.assertFalse(l.contains_point(p))
        p = [-0.0001, 0.0001]
        self.assertFalse(l.contains_point(p))


    def test_wraparound_angle(self):
        l = LinearROI([0, 0], sqrt(2), 2*pi + pi/4)
        p = [1, 1]
        self.assertTrue(l.contains_point(p))


class LinearROIDictTest(unittest.TestCase):

    def test_to_dict(self):
        l = LinearROI([1.1, 2.2], 3.3, pi/3)
        expected = {
            "typeid":"scanpointgenerator:roi/LinearROI:1.0",
            "start":[1.1, 2.2],
            "length":3.3,
            "angle":pi/3}
        self.assertEquals(expected, l.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/LinearROI:1.0",
            "start":[0, 1],
            "length":0.2,
            "angle":pi/6}
        l = LinearROI.from_dict(d)
        self.assertEqual([0.0, 1.0], l.start)
        self.assertEqual(0.2, l.length)
        self.assertEqual(pi/6, l.angle)

if __name__ == "__main__":
    unittest.main()
