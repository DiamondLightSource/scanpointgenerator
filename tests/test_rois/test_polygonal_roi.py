import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.rois.polygonal_roi import PolygonalROI
from scanpointgenerator.compat import np


class PolygonalROITests(unittest.TestCase):

    def test_init(self):
        roi = PolygonalROI([0, 0, 1], [0, 1, 0])
        self.assertEquals([0, 0, 1], roi.points_x)
        self.assertEquals([0, 1, 0], roi.points_y)

    def test_init_raises_on_few_points(self):
        with self.assertRaises(ValueError):
            roi = PolygonalROI([0, 0], [1, 1])

    def test_to_dict(self):
        roi = PolygonalROI([0, 1, 1], [0, 1, 0])
        expected = {
            "typeid":"scanpointgenerator:roi/PolygonalROI:1.0",
            "points_x":[0, 1, 1],
            "points_y":[0, 1, 0]}
        self.assertEquals(expected, roi.to_dict())

    def test_from_dict(self):
        d = {
            "typeid":"scanpointgenerator:roi/PolygonalROI:1.0",
            "points_x":[1, 1, 0],
            "points_y":[2, 3, 5]}
        roi = PolygonalROI.from_dict(d)
        self.assertEquals([1, 1, 0], roi.points_x)
        self.assertEquals([2, 3, 5], roi.points_y)

    def test_simple_point_contains(self):
        vertices_x = [0, 1, 2, 2, -1, -1]
        vertices_y = [0, 0, -1, 1, 1, -1]
        """
        Shape described looks like this:
        _____
        | _ |
        |/ \|

        """
        roi = PolygonalROI(vertices_x, vertices_y)
        p = [-0.9, -0.85]
        self.assertTrue(roi.contains_point(p))
        p = [1.9, 0.85]
        self.assertTrue(roi.contains_point(p))
        p = [0.5, -0.5]
        self.assertFalse(roi.contains_point(p))
        p = [0.5, 0.5]
        self.assertTrue(roi.contains_point(p))

    def test_complex_point_contains(self):
        vertices_x = [0, 0, 2, 2, 1, 1, 3, 3]
        vertices_y = [0, 2, 2, 1, 1, 3, 3, 0]
        roi = PolygonalROI(vertices_x, vertices_y)
        p = [0.5, 0.5]
        self.assertTrue(roi.contains_point(p))
        p = [0.5, 2.5]
        self.assertFalse(roi.contains_point(p))

        # The inner square should be "outside" according to the
        # ray-cast algorithm, even if traditionally considered "inside"
        p = [1.5, 1.5] # has winding number -2
        self.assertFalse(roi.contains_point(p))

    def test_mask_points(self):
        vertices_x = [0, 0, 2, 2, 1, 1, 3, 3]
        vertices_y = [0, 2, 2, 1, 1, 3, 3, 0]
        roi = PolygonalROI(vertices_x, vertices_y)
        px = [0.5, 0.5, 1.5, 1.5, 2.5,  2.5, 3.5, -0.5, 3.5, 2, 3, 0]
        py = [0.5, 2.5, 1.5, 2.5, 2.5, -0.5, 1.5,  0.5, 0.5, 0, 2, 1.5]
        p = [np.array(px), np.array(py)]
        points_cp = [axis.copy().tolist() for axis in p]
        expected = [True, False, False, True, True, False, False, False, False,
                    True, False, True]
        mask = roi.mask_points(p)
        self.assertEquals(expected, mask.tolist())
        self.assertEqual(points_cp, [axis.tolist() for axis in p])

if __name__ == "__main__":
    unittest.main(verbosity=2)
