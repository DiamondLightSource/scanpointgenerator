import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import ArrayGenerator


class ArrayGeneratorTest(ScanPointGeneratorTest):

    def test_1d_init(self):
        g = ArrayGenerator("x", "mm", [0, 1, 2, 3])
        self.assertEqual({"x":"mm"}, g.units)
        self.assertEqual(["x"], g.axes)

    def test_nd_init(self):
        g = ArrayGenerator(["x", "y"], ["mm", "cm"], [[0, 1], [2, 3]])
        self.assertEqual({"x":"mm", "y":"cm"}, g.units)
        self.assertEqual(["x", "y"], g.axes)

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            ArrayGenerator(["x", "y", "x"], ["mm", "mm"], [[0, 1], [1, 0]])

    def test_array_positions(self):
        points = [0., 1., 2., 2.5, 3.0, 4.0, 4.5]
        bounds = [-0.5, 0.5, 1.5, 2.25, 2.75, 3.5, 4.25, 4.75]
        g = ArrayGenerator("x", "mm", points)
        g.prepare_positions()
        g.prepare_bounds()

        self.assertEqual(points, g.positions["x"].tolist())
        self.assertEqual(bounds, g.bounds["x"].tolist())

    def test_3d_array_positions(self):
        points = [[-1, 0, 1], [-2, 0, 1], [-1, 1, 1], [3, 3, 3]]
        bounds = [[-0.5, 0, 1], [-1.5, 0, 1], [-1.5, 0.5, 1], [1, 2, 2], [5, 4, 4]]
        g = ArrayGenerator(["x", "y", "z"], ["mm", "cm", "mm"], points)
        g.prepare_positions()
        g.prepare_bounds()

        self.assertEqual([p[0] for p in points], g.positions["x"].tolist())
        self.assertEqual([p[1] for p in points], g.positions["y"].tolist())
        self.assertEqual([p[2] for p in points], g.positions["z"].tolist())
        self.assertEqual([p[0] for p in bounds], g.bounds["x"].tolist())
        self.assertEqual([p[1] for p in bounds], g.bounds["y"].tolist())
        self.assertEqual([p[2] for p in bounds], g.bounds["z"].tolist())

    def test_to_dict(self):
        points = [[0., 0.,], [1., 2.,], [0.5, 2.7], [1.3, 4.0]]
        points_flat = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]
        expected = {}
        expected["typeid"] = "scanpointgenerator:generator/ArrayGenerator:1.0"
        expected["axes"] = ["x", "y"]
        expected["units"] = ["cm", "cm"]
        expected["points"] = points_flat
        expected["alternate"] = True

        g = ArrayGenerator(["x", "y"], ["cm", "cm"], points, True)
        self.assertEqual(expected, g.to_dict())

    def test_from_dict(self):
        points = [[0., 0.,], [1., 2.,], [0.5, 2.7], [1.3, 4.0]]
        points_flat = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]

        d = {}
        d["type"] = "ArrayGenerator"
        d["axes"] = ["x", "y"]
        d["units"] = ["cm", "mm"]
        d["points"] = points_flat
        d["alternate"] = True

        g = ArrayGenerator.from_dict(d)
        self.assertEqual(["x", "y"], g.axes)
        self.assertEqual({"x":"cm", "y":"mm"}, g.units)
        self.assertEqual(points, g.points.tolist())
        self.assertEqual(True, g.alternate)

if __name__ == "__main__":
    unittest.main(verbosity=2)
