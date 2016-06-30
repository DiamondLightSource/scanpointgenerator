from collections import OrderedDict
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator import SpiralGenerator
from scanpointgenerator import LissajousGenerator
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

        gen = CompoundGenerator([self.x, self.y], [scan_region], [])

        for i, p in enumerate(gen.iterator()):
            self.assertEqual(p.positions, dict(
                x=xpositions[i], y=ypositions[i]))
            self.assertEqual(p.indexes, [xindexes[i], yindexes[i]])

    def test_mutate_called(self):
        mutator = MagicMock()
        self.g.mutators = [mutator]
        filtered = MagicMock()
        self.g._filtered_base_iterator = MagicMock()
        self.g._filtered_base_iterator.return_value = filtered

        for _ in self.g.iterator():
            pass

        mutator.mutate.assert_called_once_with(filtered)

    def test_line_spiral(self):
        positions = [{'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 0.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 0.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 0.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 2.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 2.0},
                     {'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 2.0},
                     {'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 4.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 4.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 4.0}]

        z = LineGenerator("z", "mm", 0.0, 4.0, 3)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 1.0, alternate_direction=True)
        gen = CompoundGenerator([spiral, z], [], [])

        for i, p in enumerate(gen.iterator()):
            self.assertEqual(p.positions, positions[i])

    def test_line_lissajous(self):
        positions = [{'y': 0.0, 'x': 0.5, 'z': 0.0},
                     {'y': 0.2938926261462366, 'x': 0.15450849718747375, 'z': 0.0},
                     {'y': -0.4755282581475768, 'x': -0.40450849718747367, 'z': 0.0},
                     {'y': 0.47552825814757677, 'x': -0.4045084971874738, 'z': 0.0},
                     {'y': -0.2938926261462364, 'x': 0.1545084971874736, 'z': 0.0},
                     {'y': 0.0, 'x': 0.5, 'z': 2.0},
                     {'y': 0.2938926261462366, 'x': 0.15450849718747375, 'z': 2.0},
                     {'y': -0.4755282581475768, 'x': -0.40450849718747367, 'z': 2.0},
                     {'y': 0.47552825814757677, 'x': -0.4045084971874738, 'z': 2.0},
                     {'y': -0.2938926261462364, 'x': 0.1545084971874736, 'z': 2.0},
                     {'y': 0.0, 'x': 0.5, 'z': 4.0},
                     {'y': 0.2938926261462366, 'x': 0.15450849718747375, 'z': 4.0},
                     {'y': -0.4755282581475768, 'x': -0.40450849718747367, 'z': 4.0},
                     {'y': 0.47552825814757677, 'x': -0.4045084971874738, 'z': 4.0},
                     {'y': -0.2938926261462364, 'x': 0.1545084971874736, 'z': 4.0}]

        z = LineGenerator("z", "mm", 0.0, 4.0, 3)
        box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        lissajous = LissajousGenerator(['x', 'y'], "mm", box, 1, num_points=5)
        gen = CompoundGenerator([lissajous, z], [], [])

        for i, p in enumerate(gen.iterator()):
            self.assertEqual(p.positions, positions[i])


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

        self.e1 = MagicMock()
        self.e1_dict = MagicMock()

        self.g = CompoundGenerator([self.l1, self.l2], [self.e1], [self.m1])

    def test_to_dict(self):
        self.l1.to_dict.return_value = self.l1_dict
        self.l2.to_dict.return_value = self.l2_dict
        self.e1.to_dict.return_value = self.e1_dict
        self.m1.to_dict.return_value = self.m1_dict

        gen_list = [self.l1_dict, self.l2_dict]
        mutators_list = [self.m1_dict]
        excluders_list = [self.e1_dict]

        expected_dict = OrderedDict()
        expected_dict['type'] = "CompoundGenerator"
        expected_dict['generators'] = gen_list
        expected_dict['excluders'] = excluders_list
        expected_dict['mutators'] = mutators_list

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    @patch('scanpointgenerator.compoundgenerator.Mutator')
    @patch('scanpointgenerator.compoundgenerator.Excluder')
    @patch('scanpointgenerator.compoundgenerator.Generator')
    def test_from_dict(self, gen_mock, ex_mock, mutator_mock):
        gen_mock.from_dict.side_effect = [self.l1, self.l2]
        mutator_mock.from_dict.return_value = self.m1
        ex_mock.from_dict.return_value = self.e1

        _dict = OrderedDict()
        _dict['generators'] = [self.l1_dict, self.l2_dict]
        _dict['excluders'] = [self.e1_dict]
        _dict['mutators'] = [self.m1_dict]

        units_dict = OrderedDict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = CompoundGenerator.from_dict(_dict)

        self.assertEqual(gen.generators[0], self.l1)
        self.assertEqual(gen.generators[1], self.l2)
        self.assertEqual(gen.mutators[0], self.m1)
        self.assertEqual(gen.excluders[0], self.e1)

if __name__ == "__main__":
    unittest.main()
