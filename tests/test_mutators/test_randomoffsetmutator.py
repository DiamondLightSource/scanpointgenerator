import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.compat import range_
from scanpointgenerator.generators import LineGenerator
from scanpointgenerator.mutators import RandomOffsetMutator
from scanpointgenerator import Point, CompoundGenerator

from pkg_resources import require
require("mock")
from mock import patch, MagicMock


class RandomOffsetMutatorTest(ScanPointGeneratorTest):


    def test_init(self):
        m = RandomOffsetMutator(1, ["x"], dict(x=0.25))
        self.assertEqual(1, m.seed)
        self.assertEqual(dict(x=0.25), m.max_offset)

    def test_mutate_simple(self):
        def point_gen():
            for n in range_(10):
                p = Point()
                p.indexes = [n]
                p.positions = {"x":n/10.}
                p.lower = {"x":(n-0.5)/10.}
                p.upper = {"x":(n+0.5)/10.}
                yield p
        m = RandomOffsetMutator(1, ["x"], {"x":0.01})
        original = [p for p in point_gen()]
        mutated = [m.mutate(p) for p in point_gen()]
        for o, m in zip(original, mutated):
            op, mp = o.positions["x"], m.positions["x"]
            ou, mu = o.upper["x"], m.upper["x"]
            ol, ml = o.lower["x"], m.lower["x"]
            self.assertNotEqual(op, mp)
            self.assertTrue(abs(mp - op) < 0.01)
            self.assertEqual(ou, mu)
            self.assertEqual(ol, ml)

        offsets = [m.positions["x"] - o.positions["x"] for m, o in zip(mutated, original)]
        for o1, o2 in zip(offsets[:-1], offsets[1:]):
            self.assertNotEqual(o1, o2)

    def test_random_access_consistency(self):
        def point_gen():
            for n in range_(10):
                p = Point()
                p.indexes = [n]
                p.positions = {"x":n/10.}
                p.lower = {"x":(n-0.5)/10.}
                p.upper = {"x":(n+0.5)/10.}
                yield p
        m = RandomOffsetMutator(1, ["x"], {"x":0.01})
        original = [p.positions['x'] for p in point_gen()]
        mutated1 = [m.mutate(p).positions['x'] for p in point_gen()]
        mutated2 = [m.mutate(p).positions['x'] for p in point_gen()]
        mutated3 = [m.mutate(p).positions['x'] for p in list(point_gen())[::-1]][::-1]
        self.assertNotEqual(original, mutated1)
        self.assertEqual(mutated1, mutated2)
        self.assertEqual(mutated1, mutated3)

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
