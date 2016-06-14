from collections import OrderedDict
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LineGenerator


class LineGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = LineGenerator("x", "mm", 1.0, 9.0, 5)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x"])

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


class LineGenerator2DTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [5])
        self.assertEqual(self.g.index_names, ["x", "y"])

    def test_given_inconsistent_dims_then_raise_error(self):

        with self.assertRaises(ValueError):
            LineGenerator(["x"], "mm", [1.0, 2.0], [5.0, 10.0], 5)

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

    def test_to_dict(self):
        expected_dict = OrderedDict()
        expected_dict['type'] = "LineGenerator"
        expected_dict['name'] = ['x', 'y']
        expected_dict['units'] = 'mm'
        expected_dict['start'] = [1.0, 2.0]
        expected_dict['stop'] = [5.0, 10.0]
        expected_dict['num'] = 5

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = OrderedDict()
        _dict['name'] = ['x', 'y']
        _dict['units'] = 'mm'
        _dict['start'] = [1.0, 2.0]
        _dict['stop'] = [5.0, 10.0]
        _dict['num'] = 5

        units_dict = OrderedDict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = LineGenerator.from_dict(_dict)

        self.assertEqual(['x', 'y'], gen.name)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual([1.0, 2.0], gen.start)
        self.assertEqual([5.0, 10.0], gen.stop)
        self.assertEqual(5, gen.num)

if __name__ == "__main__":
    unittest.main()



