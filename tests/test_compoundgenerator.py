from collections import OrderedDict
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import NestedGenerator
from scanpointgenerator import LineGenerator

from pkg_resources import require
require("mock")
from mock import patch, MagicMock


class NestedGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.x = LineGenerator("x", "mm", 1.0, 1.2, 3)
        self.y = LineGenerator("y", "mm", 2.0, 2.1, 2)
        self.g = NestedGenerator(self.y, self.x, alternate_direction=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(self.g.index_dims, [2, 3])
        self.assertEqual(self.g.index_names, ["y", "x"])

    def test_positions(self):
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        xlower = [0.95, 1.05, 1.15, 1.25, 1.15, 1.05]
        xupper = [1.05, 1.15, 1.25, 1.15, 1.05, 0.95]
        yindexes = [0, 0, 0, 1, 1, 1]
        xindexes = [0, 1, 2, 2, 1, 0]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(
                y=ypositions[i], x=xpositions[i]))
            self.assertEqual(p.lower, dict(
                y=ypositions[i], x=xlower[i]))
            self.assertEqual(p.upper, dict(
                y=ypositions[i], x=xupper[i]))
            self.assertEqual(p.indexes, [yindexes[i], xindexes[i]])

    def test_double_nest(self):
        self.z = LineGenerator("z", "mm", 1.0, 2.0, 2)
        self.g2 = NestedGenerator(self.z, self.g)

        zpositions = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1,
                      2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0,
                      1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        zindexes = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        yindexes = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1]
        xindexes = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0]
        for i, p in enumerate(self.g2.iterator()):
            self.assertEqual(p.positions, dict(
                z=zpositions[i], y=ypositions[i], x=xpositions[i]))
            self.assertEqual(p.indexes, [zindexes[i], yindexes[i], xindexes[i]])


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.l1 = MagicMock()
        self.l1_dict = MagicMock()

        self.l2 = MagicMock()
        self.l2_dict = MagicMock()

        self.g = NestedGenerator(self.l1, self.l2, alternate_direction=True)

    def test_to_dict(self):
        self.l1.to_dict.return_value = self.l1_dict
        self.l2.to_dict.return_value = self.l2_dict

        expected_dict = OrderedDict()
        expected_dict['type'] = "NestedGenerator"
        expected_dict['outer'] = self.l1_dict
        expected_dict['inner'] = self.l2_dict
        expected_dict['alternate_direction'] = True

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    @patch('scanpointgenerator.nestedgenerator.ScanPointGenerator')
    def test_from_dict(self, SPG_mock):
        SPG_mock.from_dict.side_effect = [self.l1, self.l2]

        _dict = OrderedDict()
        _dict['outer'] = self.l1_dict
        _dict['inner'] = self.l2_dict
        _dict['alternate_direction'] = True

        units_dict = OrderedDict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = NestedGenerator.from_dict(_dict)

        self.assertEqual(gen.outer, self.l1)
        self.assertEqual(gen.inner, self.l2)
        self.assertEqual(True, gen.alternate_direction)

if __name__ == "__main__":
    unittest.main()
