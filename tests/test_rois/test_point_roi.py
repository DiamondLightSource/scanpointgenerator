import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.point_roi import PointROI
from scanpointgenerator.compat import np


class PointROITest(unittest.TestCase):

    def test_init(self):
        roi = PointROI([1.1, 2.2])
        self.assertEqual([1.1, 2.2], roi.point)

    def test_contains_point_exact(self):
        roi = PointROI([5.4321, 1.2345])
        p = [5.4321, 1.2345]
        self.assertTrue(roi.contains_point(p))
        p = [5.4321 + 1e-15, 1.2345]
        self.assertFalse(roi.contains_point(p))
        p = [5.4321, 1.2345 + 1e-15]
        self.assertFalse(roi.contains_point(p))

    def test_contains_point_approx(self):
        roi = PointROI([1, 1])
        p = [1, 1]
        self.assertTrue(roi.contains_point(p, 1e-14))
        p = [1 + 6e-15, 1 + 6e-15]
        self.assertTrue(roi.contains_point(p, 1e-14))
        p = [1 + 1e-14, 1 + 1e-14]
        self.assertFalse(roi.contains_point(p, 1e-14))

    def test_mask_points(self):
        roi = PointROI([1, 2])
        px = [1, 0, 1+1e-15, 1,       1]
        py = [2, 0, 2,       2+1e-15, 2+1e-14]
        expected = [True, False, True, True, False]
        p = [np.array(px), np.array(py)]
        points_cp = [axis.copy().tolist() for axis in p]
        mask = roi.mask_points(p, 2e-15)
        self.assertEqual(expected, mask.tolist())

        mask = roi.mask_points([np.array(px), np.array(py)], 0)
        expected = [True, False, False, False, False]
        self.assertEqual(expected, mask.tolist())
        self.assertEqual(points_cp, [axis.tolist() for axis in p])

    def test_to_dict(self):
        roi = PointROI([1.1, 2.2])
        expected = {
            "typeid":"scanpointgenerator:roi/PointROI:1.0",
            "point":[1.1, 2.2]}
        self.assertEqual(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/PointROI:1.0",
            "point":[0.1, 0.2]}
        roi = PointROI.from_dict(d)
        self.assertEqual([0.1, 0.2], roi.point)

if __name__ == "__main__":
    unittest.main()
