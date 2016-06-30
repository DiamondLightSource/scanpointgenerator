from collections import OrderedDict
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator.excluder import Excluder
from scanpointgenerator.circular_roi import CircularROI

from pkg_resources import require
require("mock")
from mock import patch, MagicMock


class CompoundGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        self.y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        self.z = LineGenerator("z", "mm", 1.0, 2.0, 2, False)
        self.g = CompoundGenerator([self.x, self.y], [], [])

    def test_init(self):
        self.assertEqual(self.g.generators[0], self.x)
        self.assertEqual(self.g.generators[1], self.y)
        self.assertEqual(self.g.num_points, 6)
        self.assertEqual(self.g.lengths, [3, 2])
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [3, 2])
        self.assertEqual(self.g.index_names, ["x", "y"])

    def test_contains_point_true(self):
        point = MagicMock()
        point.positions.__getitem__.side_effect = [1.0, 2.0]
        roi = MagicMock()
        roi.contains_point.return_value = True
        region = MagicMock()
        region.scannables = ['x', 'y']
        region.roi = roi
        self.g.excluders = [region]

        response = self.g.contains_point(point)

        call_list = [call[0][0] for call in point.positions.__getitem__.call_args_list]
        self.assertIn('x', call_list)
        self.assertIn('y', call_list)
        roi.contains_point.assert_called_once_with([1.0, 2.0])
        self.assertTrue(response)

    def test_contains_point_false(self):
        point = MagicMock()
        point.positions.__getitem__.side_effect = [1.0, 2.0]
        roi = MagicMock()
        roi.contains_point.return_value = False
        region = MagicMock()
        region.scannables = ['x', 'y']
        region.roi = roi
        self.g.excluders = [region]

        response = self.g.contains_point(point)

        call_list = [call[0][0] for call in point.positions.__getitem__.call_args_list]
        self.assertIn('x', call_list)
        self.assertIn('y', call_list)
        roi.contains_point.assert_called_once_with([1.0, 2.0])
        self.assertFalse(response)

    def test_positions(self):
        xlower = [0.95, 1.05, 1.15, 1.25, 1.15, 1.05]
        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        xupper = [1.05, 1.15, 1.25, 1.15, 1.05, 0.95]
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        xindexes = [0, 1, 2, 2, 1, 0]
        yindexes = [0, 0, 0, 1, 1, 1]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.upper['x'], xupper[i])
            self.assertEqual(p.lower['x'], xlower[i])
            self.assertEqual(p.positions, dict(x=xpositions[i], y=ypositions[i]))
            self.assertEqual(p.indexes, [xindexes[i], yindexes[i]])

    def test_double_nest(self):
        self.g = CompoundGenerator([self.x, self.y, self.z], [], [])

        xpositions = [1.0, 1.1, 1.2, 1.2, 1.1, 1.0,
                      1.0, 1.1, 1.2, 1.2, 1.1, 1.0]
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1, 2.1,
                      2.0, 2.0, 2.0, 2.1, 2.1, 2.1]
        zpositions = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
        xindexes = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0]
        yindexes = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1]
        zindexes = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, dict(
                x=xpositions[i], y=ypositions[i], z=zpositions[i]))
            self.assertEqual(p.indexes, [xindexes[i], yindexes[i], zindexes[i]])

    def test_iterator_with_region(self):
        xpositions = [1.0, 1.1, 1.2, 1.1, 1.0]
        ypositions = [2.0, 2.0, 2.0, 2.1, 2.1]
        xindexes = [0, 1, 2, 1, 0]
        yindexes = [0, 0, 0, 1, 1]

        circle = CircularROI([1.0, 2.0], 0.2)
        scan_region = Excluder(circle, ['x', 'y'])

        gen = CompoundGenerator([self.x, self.y], [], [scan_region])

        for i, p in enumerate(gen.iterator()):
            self.assertEqual(p.positions, dict(
                x=xpositions[i], y=ypositions[i]))
            self.assertEqual(p.indexes, [xindexes[i], yindexes[i]])


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.l1 = MagicMock()
        self.l1.name = ['x']
        self.l1_dict = MagicMock()

        self.l2 = MagicMock()
        self.l2.name = ['y']
        self.l2_dict = MagicMock()

        self.m1 = MagicMock()
        self.m1_dict = MagicMock()

        self.r1 = MagicMock()
        self.r1_dict = MagicMock()

        self.g = CompoundGenerator([self.l1, self.l2], [self.m1], [self.r1])

    def test_to_dict(self):
        self.l1.to_dict.return_value = self.l1_dict
        self.l2.to_dict.return_value = self.l2_dict
        self.r1.to_dict.return_value = self.r1_dict
        self.m1.to_dict.return_value = self.m1_dict

        gen_list = [self.l1_dict, self.l2_dict]
        mutators_list = [self.m1_dict]
        region_list = [self.r1_dict]

        expected_dict = OrderedDict()
        expected_dict['type'] = "CompoundGenerator"
        expected_dict['generators'] = gen_list
        expected_dict['mutators'] = mutators_list
        expected_dict['regions'] = region_list

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    @patch('scanpointgenerator.compoundgenerator.Mutator')
    @patch('scanpointgenerator.compoundgenerator.Excluder')
    @patch('scanpointgenerator.compoundgenerator.Generator')
    def test_from_dict(self, gen_mock, ex_mock, mutator_mock):
        gen_mock.from_dict.side_effect = [self.l1, self.l2]
        mutator_mock.from_dict.return_value = self.m1
        ex_mock.from_dict.return_value = self.r1

        _dict = OrderedDict()
        _dict['generators'] = [self.l1_dict, self.l2_dict]
        _dict['mutators'] = [self.m1_dict]
        _dict['regions'] = [self.r1_dict]

        units_dict = OrderedDict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = CompoundGenerator.from_dict(_dict)

        self.assertEqual(gen.generators[0], self.l1)
        self.assertEqual(gen.generators[1], self.l2)
        self.assertEqual(gen.mutators[0], self.m1)
        self.assertEqual(gen.excluders[0], self.r1)

if __name__ == "__main__":
    unittest.main()
