import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
from math import pi

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.sector_roi import SectorROI


class SectorInitTest(unittest.TestCase):

    def test_init(self):
        s = SectorROI([1.1, 2.2], [3.3, 4.4], [pi/2, 2*pi])
        self.assertEquals([1.1, 2.2], s.centre)
        self.assertEquals([3.3, 4.4], s.radii)
        self.assertEquals([pi/2, 2*pi], s.angles)

    def test_init_negative_range(self):
        s = SectorROI([0, 0], [0, 1], [pi/2, -pi/2])
        self.assertEquals([pi/2, 3*pi/2], s.angles)

    def test_invalid_radii_fails(self):
        with self.assertRaises(ValueError):
            s = SectorROI([0, 0], [-1, 1], [0, 0])
        with self.assertRaises(ValueError):
            s = SectorROI([0, 0], [1, 0], [0, 0])
        with self.assertRaises(ValueError):
            s = SectorROI([0, 0], [-2, -3], [0, 0])

class SectorDictTest(unittest.TestCase):

    def test_to_dict(self):
        s = SectorROI([1.1, 2.2], [3.3, 4.4], [pi/2, pi])
        expected = {
            "typeid":"scanpointgenerator:roi/SectorROI:1.0",
            "centre":[1.1, 2.2],
            "radii":[3.3, 4.4],
            "angles":[pi/2, pi]}
        self.assertEquals(expected, s.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/SectorROI:1.0",
            "centre":[0.1, 0.2],
            "radii":[1, 2],
            "angles":[0, pi]}
        s = SectorROI.from_dict(d)
        self.assertEqual([0.1, 0.2], s.centre)
        self.assertEqual([1, 2], s.radii)
        self.assertEqual([0, pi], s.angles)

class SectorContainsTest(unittest.TestCase):

    def test_inner_disc_fails(self):
        s = SectorROI((0, 0), (1., 2.), (0, 2*pi))
        p = (0.9, 0)
        self.assertFalse(s.contains_point(p))
        p = (0, 0.9)
        self.assertFalse(s.contains_point(p))
        p = (0.7, 0.7) # < (sqrt(2)/2, sqrt(2)/2)
        self.assertFalse(s.contains_point(p))
        p = (-0.7, -0.7)
        self.assertFalse(s.contains_point(p))

    def test_outside_disc_fails(self):
        s = SectorROI((0, 0), (1., 2.), (0, 2*pi))
        p = (2.1, 0)
        self.assertFalse(s.contains_point(p))
        p = (0, 2.1)
        self.assertFalse(s.contains_point(p))
        p = (1.5, 1.5) # > (sqrt(2), sqrt(2))
        self.assertFalse(s.contains_point(p))
        p = (-1.5, 1.5)
        self.assertFalse(s.contains_point(p))

    def test_inside_disc_passes(self):
        s = SectorROI((0, 0), (1., 2.), (0, 2*pi))
        p = (1, 0)
        self.assertTrue(s.contains_point(p))
        p = (2, 0)
        self.assertTrue(s.contains_point(p))
        p = (1, 1)
        self.assertTrue(s.contains_point(p))
        p = (-1, -1)
        self.assertTrue(s.contains_point(p))

    def test_past_sector_fail(self):
        s = SectorROI((0, 0), (0, 1), (0, pi))
        p = (-0.1, -0.1)
        self.assertFalse(s.contains_point(p))
        p = (0.1, -0.1)
        self.assertFalse(s.contains_point(p))
        s = SectorROI((0, 0), (0, 1), (pi, 0))
        p = (-0.1, 0.1)
        self.assertFalse(s.contains_point(p))
        p = (0.1, 0.1)
        self.assertFalse(s.contains_point(p))

    def test_in_sector_passes(self):
        s = SectorROI((0, 0), (0, 1), (0, pi/2))
        p = (1, 0)
        self.assertTrue(s.contains_point(p))
        p = (0, 1)
        self.assertTrue(s.contains_point(p))
        p = (0.7, 0.7)
        self.assertTrue(s.contains_point(p))

        s = SectorROI((0, 0), (0, 1), (pi, 3*pi/2))
        p = (-1, 0)
        self.assertTrue(s.contains_point(p))
        p = (0, -1)
        self.assertTrue(s.contains_point(p))
        p = (-0.7, -0.7)
        self.assertTrue(s.contains_point(p))

    def test_large_ranges_pass(self):
        s = SectorROI((0, 0), (0, 1), (-pi, 5*pi))
        p = (0.7, 0.7)
        self.assertTrue(s.contains_point(p))

    def test_negative_ranges(self):
        s = SectorROI((0, 0), (0, 1), (pi/2, -pi/2))
        s.angles = (pi/2, -pi/2)
        p = (0.1, 0)
        self.assertFalse(s.contains_point(p))
        p = (-0.1, 0)
        self.assertTrue(s.contains_point(p))

        s = SectorROI((0, 0), (0, 1), (-pi/2, pi/2))
        p = (-0.1, 0)
        self.assertFalse(s.contains_point(p))
        p = (0.1, 0)
        self.assertTrue(s.contains_point(p))

        s = SectorROI((0, 0), (0, 1), (pi, -6*pi))
        s.angles = (pi, -6*pi)
        p = (1, 0)
        self.assertTrue(s.contains_point(p))
        p = (0, 1)
        self.assertTrue(s.contains_point(p))
        p = (-1, 0)
        self.assertTrue(s.contains_point(p))
        p = (0, -1)
        self.assertTrue(s.contains_point(p))

if __name__ == "__main__":
    unittest.main()
