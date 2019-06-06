import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import ArrayGenerator


class ArrayGeneratorTest(ScanPointGeneratorTest):

    def test_1d_init(self):
        g = ArrayGenerator("x", "mm", [0, 1, 2, 3])
        self.assertEqual({"x":"mm"}, g.axis_units())
        self.assertEqual(["x"], g.axes)

    def test_array_positions(self):
        points = [0., 1., 2., 2.5, 3.0, 4.0, 4.5]
        bounds = [-0.5, 0.5, 1.5, 2.25, 2.75, 3.5, 4.25, 4.75]
        g = ArrayGenerator("x", "mm", points)
        g.prepare_positions()
        g.prepare_bounds()

        self.assertEqual(points, g.positions["x"].tolist())
        self.assertEqual(bounds, g.bounds["x"].tolist())

    def test_to_dict(self):
        points = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]
        expected = {}
        expected["typeid"] = "scanpointgenerator:generator/ArrayGenerator:1.0"
        expected['axes'] = ["x"]
        expected["units"] = ["cm"]
        expected["points"] = points
        expected["alternate"] = True

        g = ArrayGenerator("x", "cm", points, True)

        self.assertEqual(expected, g.to_dict())

    def test_from_dict(self):
        points = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]

        d = {}
        d["axes"] = ["x"]
        d["units"] = "cm"
        d["points"] = points
        d["alternate"] = True

        g = ArrayGenerator.from_dict(d)
        self.assertEqual(["x"], g.axes)
        self.assertEqual({"x":"cm"}, g.axis_units())
        self.assertEqual(points, g.points)
        self.assertEqual(True, g.alternate)

    def test_from_dict_backwards_compatible(self):
        points = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]

        d = {}
        d["axis"] = ["x"]
        d["units"] = "cm"
        d["points"] = points
        d["alternate"] = True

        g = ArrayGenerator.from_dict(d)
        self.assertEqual(["x"], g.axes)
        self.assertEqual({"x":"cm"}, g.axis_units())
        self.assertEqual(points, g.points)
        self.assertEqual(True, g.alternate)

    def test_from_dict_extra_args_asserts(self):
        points = [0., 0., 1., 2., 0.5, 2.7, 1.3, 4.0]

        d = {}
        d["axes"] = ["x"]
        d["units"] = "cm"
        d["points"] = points
        d["alternate"] = True
        d["extra"] = ["extra_argument"]

        with self.assertRaises(AssertionError):
            ArrayGenerator.from_dict(d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
