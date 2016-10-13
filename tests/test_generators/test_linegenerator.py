import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LineGenerator


class LineGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate_direction=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x"])
        self.assertEqual(self.g.axes, ["x"])

    def test_iterator(self):
        positions = [1.0, 3.0, 5.0, 7.0, 9.0]
        lower = [0.0, 2.0, 4.0, 6.0, 8.0]
        upper = [2.0, 4.0, 6.0, 8.0, 10.0]
        indexes = [0, 1, 2, 3, 4]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(x=positions[i]))
            self.assertEqual(p.lower, dict(x=lower[i]))
            self.assertEqual(p.upper, dict(x=upper[i]))
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            LineGenerator(["x", "x"], "mm", 0.0, 1.0, 5)

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/LineGenerator:1.0"
        expected_dict['name'] = ["x"]
        expected_dict['units'] = "mm"
        expected_dict['start'] = [1.0]
        expected_dict['stop'] = [9.0]
        expected_dict['num'] = 5
        expected_dict['alternate_direction'] = True

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()
        _dict['name'] = ["x"]
        _dict['units'] = "mm"
        _dict['start'] = [1.0]
        _dict['stop'] = [9.0]
        _dict['num'] = 5
        _dict['alternate_direction'] = True

        units_dict = dict()
        units_dict['x'] = "mm"

        gen = LineGenerator.from_dict(_dict)

        self.assertEqual(["x"], gen.name)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual([1.0], gen.start)
        self.assertEqual([9.0], gen.stop)
        self.assertEqual(5, gen.num)
        self.assertTrue(gen.alternate_direction)


class LineGenerator2DTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x_y_Line"])
        self.assertEqual(self.g.axes, ["x", "y"])

    def test_given_inconsistent_dims_then_raise_error(self):

        with self.assertRaises(ValueError):
            LineGenerator("x", "mm", [1.0], [5.0, 10.0], 5)

    def test_give_one_point_then_step_zero(self):
        l = LineGenerator(["1", "2", "3", "4", "5"], "mm", [0.0]*5, [10.0]*5, 1)
        self.assertEqual(l.step, [0]*5)

    def test_iterator(self):
        x_positions = [1.0, 2.0, 3.0, 4.0, 5.0]
        y_positions = [2.0, 4.0, 6.0, 8.0, 10.0]
        lower = [0.5, 1.5, 2.5, 3.5, 4.5]
        upper = [1.5, 2.5, 3.5, 4.5, 5.5]
        indexes = [0, 1, 2, 3, 4]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(x=x_positions[i],
                                               y=y_positions[i]))
            self.assertEqual(p.lower["x"], lower[i])
            self.assertEqual(p.upper["x"], upper[i])
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)

if __name__ == "__main__":
    unittest.main()



