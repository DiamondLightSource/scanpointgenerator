import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import ArrayGenerator

from pkg_resources import require
require("mock")
from mock import patch


class LineGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        test_array = [[0.0, 0.0], [1.0, 5.0], [2.0, 10.0], [3.0, 15.0]]
        self.g = ArrayGenerator(["x", "y"], "mm", test_array)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [4])
        self.assertEqual(self.g.index_names, ["x", "y"])
        self.assertEqual(self.g.axes, ["x", "y"])

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            ArrayGenerator(["x", "x"], "mm", [0.0, 1.0])

    def test_init_with_simple_name_and_points(self):
        g = ArrayGenerator("x", "mm", [1.0, 2.0, 3.0],
                                      [0.5, 1.5, 2.5],
                                      [1.5, 2.5, 3.5])
        self.assertEqual(g.position_units, dict(x="mm"))
        self.assertEqual(g.index_dims, [3])
        self.assertEqual(g.index_names, ["x"])
        self.assertEqual(g.points, [[1.0], [2.0], [3.0]])
        self.assertEqual(g.lower_bounds, [[0.5], [1.5], [2.5]])
        self.assertEqual(g.upper_bounds, [[1.5], [2.5], [3.5]])

    def test_inconsistent_dimensions_raises(self):
        with self.assertRaises(ValueError):
            ArrayGenerator(["x"], "mm", [[0.0, 1.0], [2.0, 3.0]])
        with self.assertRaises(ValueError):
            ArrayGenerator(["x"], "mm", [[0.0], [1.0], [2.0]],
                           lower_bounds=[[0.0, 1.0], [2.0, 3.0]])
        with self.assertRaises(ValueError):
            ArrayGenerator(["x"], "mm", [[0.0], [1.0], [2.0]],
                           upper_bounds=[[0.0, 1.0], [2.0, 3.0]])

    def test_calculate_first_lower_bound(self):
        new_bound = self.g._calculate_lower_bound(0, 0, 0.0)
        self.assertEqual(-0.5, new_bound)

    def test_calculate_other_lower_bound(self):
        new_bound = self.g._calculate_lower_bound(2, 0, 2.0)
        self.assertEqual(1.5, new_bound)

    def test_calculate_last_upper_bound(self):
        new_bound = self.g._calculate_upper_bound(3, 0, 3.0)
        self.assertEqual(3.5, new_bound)

    def test_calculate_other_upper_bound(self):
        new_bound = self.g._calculate_upper_bound(1, 0, 1.0)
        self.assertEqual(1.5, new_bound)

    @patch('scanpointgenerator.arraygenerator.ArrayGenerator._calculate_lower_bound')
    @patch('scanpointgenerator.arraygenerator.ArrayGenerator._calculate_upper_bound')
    def test_iterator_without_bounds(self, upper_mock, lower_mock):
        upper_mock.side_effect = [0.5, 2.5, 1.5, 7.5, 2.5, 12.5, 3.5, 17.5]
        lower_mock.side_effect = [-0.5, -2.5, 0.5, 2.5, 1.5, 7.5, 2.5, 12.5]

        positions = [[0.0, 0.0], [1.0, 5.0], [2.0, 10.0], [3.0, 15.0]]
        lower = [[-0.5, -2.5], [0.5, 2.5], [1.5, 7.5], [2.5, 12.5]]
        upper = [[0.5, 2.5], [1.5, 7.5], [2.5, 12.5], [3.5, 17.5]]
        indexes = [0, 1, 2, 3]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions,
                             dict(x=positions[i][0], y=positions[i][1]))
            self.assertEqual(p.lower, dict(x=lower[i][0], y=lower[i][1]))
            self.assertEqual(p.upper, dict(x=upper[i][0], y=upper[i][1]))
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 3)

    def test_iterator_with_bounds(self):
        self.g.lower_bounds = [[-0.5, -2.5], [0.5, 2.5], [1.5, 7.5], [2.5, 12.5]]
        self.g.upper_bounds = [[0.5, 2.5], [1.5, 7.5], [2.5, 12.5], [3.5, 17.5]]

        positions = [[0.0, 0.0], [1.0, 5.0], [2.0, 10.0], [3.0, 15.0]]
        lower = [[-0.5, -2.5], [0.5, 2.5], [1.5, 7.5], [2.5, 12.5]]
        upper = [[0.5, 2.5], [1.5, 7.5], [2.5, 12.5], [3.5, 17.5]]
        indexes = [0, 1, 2, 3]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions,
                             dict(x=positions[i][0], y=positions[i][1]))
            self.assertEqual(p.lower, dict(x=lower[i][0], y=lower[i][1]))
            self.assertEqual(p.upper, dict(x=upper[i][0], y=upper[i][1]))
            self.assertEqual(p.indexes, [indexes[i]])

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/ArrayGenerator:1.0"
        expected_dict['name'] = ['x', 'y']
        expected_dict['units'] = 'mm'
        expected_dict['points'] = [[0.0, 0.0], [1.0, 5.0], [2.0, 10.0], [3.0, 15.0]]
        expected_dict['lower_bounds'] = None
        expected_dict['upper_bounds'] = None

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        points = [[0.0, 0.0], [1.0, 5.0], [2.0, 10.0], [3.0, 15.0]]
        _dict = dict()
        _dict['name'] = ['x', 'y']
        _dict['units'] = 'mm'
        _dict['points'] = points
        _dict['lower_bounds'] = None
        _dict['upper_bounds'] = None

        units_dict = dict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = ArrayGenerator.from_dict(_dict)

        self.assertEqual(['x', 'y'], gen.name)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual(points, gen.points)
        self.assertIsNone(gen.lower_bounds)
        self.assertIsNone(gen.upper_bounds)

if __name__ == "__main__":
    unittest.main()



