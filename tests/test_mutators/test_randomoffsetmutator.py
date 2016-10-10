import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.mutators import RandomOffsetMutator
from scanpointgenerator.generators import LineGenerator
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import Point

from pkg_resources import require
require("mock")
from mock import patch, MagicMock


class RandomOffsetMutatorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.line_gen = LineGenerator("x", "mm", 1.0, 5.0, 5)
        self.m = RandomOffsetMutator(1, ["x"], dict(x=0.25))

    def test_init(self):
        self.assertEqual(1, self.m.seed)
        self.assertEqual(dict(x=0.25), self.m.max_offset)

    def test_get_random_number(self):
        number = self.m.get_random_number()
        self.assertEqual(0.48590197099999966, number)
        number = self.m.get_random_number()
        self.assertEqual(0.3167828240000006, number)
        number = self.m.get_random_number()
        self.assertEqual(-0.7892260970000002, number)

    @patch('scanpointgenerator.mutators.RandomOffsetMutator.get_random_number',
           return_value=1.0)
    def test_apply_offset(self, _):
        point = MagicMock()
        point.positions = dict(x=1.0)

        response = self.m.apply_offset(point)

        self.assertTrue(response)
        self.assertEqual(dict(x=1.25), point.positions)

    @patch('scanpointgenerator.mutators.RandomOffsetMutator.get_random_number',
           return_value=1.0)
    def test_apply_offset_unchanged(self, _):
        point = MagicMock()
        point.positions = dict(x=1.0)
        self.m.max_offset = dict(x=0.0)

        response = self.m.apply_offset(point)

        self.assertFalse(response)
        self.assertEqual(dict(x=1.0), point.positions)

    def test_calculate_new_bounds(self):
        current_point = Point()
        current_point.positions = dict(x=1.0)
        current_point.upper = dict(x=1.1)
        next_point = Point()
        next_point.positions = dict(x=2.0)

        self.m.calculate_new_bounds(current_point, next_point)

        self.assertEqual(dict(x=1.5), current_point.upper)
        self.assertEqual(dict(x=1.5), next_point.lower)

    def test_mutate(self):
        positions = [1.12147549275, 2.079195706,
                     2.80269347575, 3.908258751, 5.23701473025]
        lower = [0.5, 1.600335599375,
                 2.440944590875, 3.355476113375, 4.572636740625]
        upper = [1.600335599375, 2.440944590875,
                 3.355476113375, 4.572636740625, 5.5]
        indexes = [0, 1, 2, 3, 4]

        for i, p in enumerate(self.m.mutate(self.line_gen.iterator())):
            self.assertAlmostEqual(p.positions['x'], positions[i], places=10)
            self.assertAlmostEqual(p.lower['x'], lower[i], places=10)
            self.assertAlmostEqual(p.upper['x'], upper[i], places=10)
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 4)

    def test_order_of_offsets(self):
        line1 = LineGenerator("y", "mm", 2.0, 10.0, 5)
        line2 = LineGenerator("x", "mm", 1.0, 5.0, 5)

        mutator = RandomOffsetMutator(1, ["y", "x"], dict(x=0.25, y=0.25))
        gen = CompoundGenerator([line1, line2], [], [mutator])
        p = next(gen.iterator())
        self.assertAlmostEqual(p.positions['x'], 1.0791957060000001, places=10)
        self.assertAlmostEqual(p.positions['y'], 2.12147549275, places=10)

        # Swap order of axes in mutator; should swap offsets applied to x and y
        mutator = RandomOffsetMutator(1, ["x", "y"], dict(x=0.25, y=0.25))
        gen = CompoundGenerator([line1, line2], [], [mutator])
        p = next(gen.iterator())
        self.assertAlmostEqual(p.positions['x'], 1.12147549275, places=10)
        self.assertAlmostEqual(p.positions['y'], 2.0791957060000001, places=10)


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.l = MagicMock()
        self.l_dict = MagicMock()
        self.max_offset = dict(x=0.25)

        self.m = RandomOffsetMutator(1, ["x"], self.max_offset)

    def test_to_dict(self):
        self.l.to_dict.return_value = self.l_dict

        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:mutator/RandomOffsetMutator:1.0"
        expected_dict['seed'] = 1
        expected_dict['axes'] = ["x"]
        expected_dict['max_offset'] = self.max_offset

        d = self.m.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):

        _dict = dict()
        _dict['seed'] = 1
        _dict['axes'] = ["x"]
        _dict['max_offset'] = self.max_offset

        units_dict = dict()
        units_dict['x'] = 'mm'

        m = RandomOffsetMutator.from_dict(_dict)

        self.assertEqual(1, m.seed)
        self.assertEqual(self.max_offset, m.max_offset)


if __name__ == "__main__":
    unittest.main()
