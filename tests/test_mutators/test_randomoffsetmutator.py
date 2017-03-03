import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.compat import range_
from scanpointgenerator.generators import LineGenerator, LissajousGenerator
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
        mutated = [m.mutate(p, i) for i, p in enumerate(point_gen())]
        for o, m in zip(original, mutated):
            op, mp = o.positions["x"], m.positions["x"]
            ou, mu = o.upper["x"], m.upper["x"]
            ol, ml = o.lower["x"], m.lower["x"]
            self.assertNotEqual(op, mp)
            self.assertTrue(abs(mp - op) < 0.01)
            self.assertTrue(abs(mu - ou) < 0.01)
            self.assertTrue(abs(ml - ol) < 0.01)

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
        m = RandomOffsetMutator(5025, ["x"], {"x":0.01})
        original = [p.positions['x'] for p in point_gen()]
        mutated1 = [m.mutate(p, i).positions['x'] for i, p in enumerate(point_gen())]
        mutated2 = [m.mutate(p, i).positions['x'] for i, p in enumerate(point_gen())]
        mutated3 = [m.mutate(p, i).positions['x'] for i, p in list(enumerate(point_gen()))[::-1]][::-1]
        self.assertNotEqual(original, mutated1)
        self.assertEqual(mutated1, mutated2)
        self.assertEqual(mutated1, mutated3)

    def test_bounds_consistency(self):
        def point_gen():
            for n in range_(10):
                p = Point()
                p.indexes = [n]
                p.positions = {"x":n/10.}
                p.lower = {"x":(n-0.5)/10.}
                p.upper = {"x":(n+0.5)/10.}
                yield p
        m = RandomOffsetMutator(1, ["x"], {"x":0.01})
        original = [p.positions["x"] for p in point_gen()]
        mutated = [m.mutate(p, i) for i, p in enumerate(point_gen())]
        for m1, m2 in zip(mutated[:-1], mutated[1:]):
            self.assertEqual(m1.upper["x"], m2.lower["x"])

    def test_double_line_consistency(self):
        xg = LineGenerator("x", "mm", 0, 4, 5, True)
        yg = LineGenerator("y", "mm", 0, 4, 3)
        m = RandomOffsetMutator(1, ["x", "y"], {"x":0.1, "y":0.25})
        g = CompoundGenerator([yg, xg], [], [])
        g.prepare()
        points = list(g.iterator())
        ly = [l.upper["y"] for l in points[0:4] + points[5:9] + points[10:14]]
        ry = [r.lower["y"] for r in points[1:5] + points[6:10] + points[11:15]]
        self.assertEqual(ly, ry)

    def test_bounds_consistency_in_compound(self):
        liss = LissajousGenerator(["x", "y"], ["mm", "mm"], [0., 0.], [2., 2.],
             4, 100, True)
        line = LineGenerator("z", "mm", 0, 1, 3)
        m = RandomOffsetMutator(1, ["x", "y"], {"x":0.1, "y":0.1})
        g = CompoundGenerator([line, liss], [], [])
        gm = CompoundGenerator([line, liss], [], [m])
        g.prepare()
        gm.prepare()
        points = list(gm.iterator())
        lx = [l.upper["x"] for l in points[:-1]]
        rx = [r.lower["x"] for r in points[1:]]
        self.assertListAlmostEqual(lx, rx)
        ly = [l.upper["y"] for l in points[:-1]]
        ry = [r.lower["y"] for r in points[1:]]
        self.assertListAlmostEqual(ly, ry)

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
    unittest.main(verbosity=2)
