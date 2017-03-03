import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LineGenerator


class LineGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        g = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate=True)
        self.assertEqual(dict(x="mm"), g.units)
        self.assertEqual(["x"], g.axes)
        self.assertEqual(True, g.alternate)

    def test_init_multi_dim(self):
        g = LineGenerator(["x", "y"], ["mm", "cm"], [2., -2.], [4., -4.], 3)
        self.assertEqual(["x", "y"], g.axes)
        self.assertEqual({"x":"mm", "y":"cm"}, g.units)
        self.assertEqual(False, g.alternate)

    def test_array_positions(self):
        g = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate=True)
        positions = [1.0, 3.0, 5.0, 7.0, 9.0]
        bounds = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
        indexes = [0, 1, 2, 3, 4]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(positions, g.positions['x'].tolist())
        self.assertEqual(bounds, g.bounds['x'].tolist())

    def test_negative_direction(self):
        g = LineGenerator("x", "mm", 2, -2, 5)
        positions = [2., 1., 0., -1., -2.]
        bounds = [2.5, 1.5, 0.5, -0.5, -1.5, -2.5]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(positions, g.positions['x'].tolist())
        self.assertEqual(bounds, g.bounds['x'].tolist())

    def test_single_point(self):
        g = LineGenerator("x", "mm", 1.0, 4.0, 1)
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual([1.0], g.positions["x"].tolist())
        self.assertEqual([-0.5, 2.5], g.bounds["x"].tolist())

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            LineGenerator(["x", "x"], "mm", 0.0, 1.0, 5)

    def test_to_dict(self):
        g = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate=True)
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/LineGenerator:1.0"
        expected_dict['axes'] = ["x"]
        expected_dict['units'] = ["mm"]
        expected_dict['start'] = [1.0]
        expected_dict['stop'] = [9.0]
        expected_dict['size'] = 5
        expected_dict['alternate'] = True

        d = g.to_dict()
        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()
        _dict['axes'] = ["x"]
        _dict['units'] = ["mm"]
        _dict['start'] = [1.0]
        _dict['stop'] = [9.0]
        _dict['size'] = 5
        _dict['alternate'] = True

        units_dict = dict()
        units_dict['x'] = "mm"

        gen = LineGenerator.from_dict(_dict)

        self.assertEqual(["x"], gen.axes)
        self.assertEqual(units_dict, gen.units)
        self.assertEqual([1.0], gen.start)
        self.assertEqual([9.0], gen.stop)
        self.assertEqual(5, gen.size)
        self.assertTrue(gen.alternate)

class LineGenerator2DTest(ScanPointGeneratorTest):

    def test_init(self):
        g = LineGenerator(["x", "y"], ["mm", "mm"], [1.0, 2.0], [5.0, 10.0], 5)
        self.assertEqual(dict(x="mm", y="mm"), g.units)
        self.assertEqual(["x", "y"], g.axes)

    def test_given_inconsistent_dims_then_raise_error(self):
        with self.assertRaises(ValueError):
            LineGenerator("x", "mm", [1.0], [5.0, 10.0], 5)

    def test_give_one_point_then_step_zero(self):
        l = LineGenerator(["1", "2", "3", "4", "5"], "mm", [0.0]*5, [10.0]*5, 1)
        self.assertEqual([0]*5, l.step)

    def test_array_positions(self):
        g = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)
        g.prepare_positions()
        g.prepare_bounds()
        x_positions = [1.0, 2.0, 3.0, 4.0, 5.0]
        y_positions = [2.0, 4.0, 6.0, 8.0, 10.0]
        x_bounds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
        y_bounds = [1, 3, 5, 7, 9, 11]
        self.assertEqual(x_positions, g.positions['x'].tolist())
        self.assertEqual(y_positions, g.positions['y'].tolist())
        self.assertEqual(x_bounds, g.bounds['x'].tolist())
        self.assertEqual(y_bounds, g.bounds['y'].tolist())

if __name__ == "__main__":
    unittest.main(verbosity=2)
