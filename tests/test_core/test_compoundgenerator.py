import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator, Mutator, Generator, Excluder
from scanpointgenerator import LineGenerator
from scanpointgenerator import SpiralGenerator
from scanpointgenerator import LissajousGenerator
from scanpointgenerator import StaticPointGenerator
from scanpointgenerator import ROIExcluder
from scanpointgenerator import SquashingExcluder
from scanpointgenerator.rois import CircularROI, RectangularROI, EllipticalROI, SectorROI, PolygonalROI
from scanpointgenerator.mutators import RandomOffsetMutator
from scanpointgenerator.compat import range_, np

from pkg_resources import require
require("mock")
from mock import patch, MagicMock, ANY


class CompoundGeneratorTest(ScanPointGeneratorTest):
    def test_init(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        g = CompoundGenerator([y, x], [], [], 0.2, False)
        self.assertEqual(g.generators[0], y)
        self.assertEqual(g.generators[1], x)
        self.assertEqual(g.units, dict(y="mm", x="mm"))
        self.assertEqual(g.axes, ["y", "x"])
        self.assertEqual(g.duration, 0.2)

    def test_default_init_values(self):
        g = CompoundGenerator([], [], [])
        self.assertEqual(-1, g.duration)
        self.assertEqual(True, g.continuous)

    def test_given_compound_raise_error(self):
        g = CompoundGenerator([], [], [])
        with self.assertRaises(AssertionError):
            CompoundGenerator([g], [], [])

    def test_duplicate_name_raises(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("x", "mm", 2.0, 2.1, 2, False)
        with self.assertRaises(ValueError):
            CompoundGenerator([y, x], [], [])

    def test_raise_before_prepare(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        g = CompoundGenerator([x], [], [])
        with self.assertRaises(ValueError):
            g.get_point(0)
        with self.assertRaises(ValueError):
            for p in g.iterator(): pass

    def test_prepare_idempotent(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        g = CompoundGenerator([x], [], [])
        x.prepare_positions = MagicMock(return_value=x.prepare_positions())
        g.prepare()
        x.prepare_positions.assert_called_once_with()
        x.prepare_positions.reset_mock()
        g.prepare()
        x.prepare_positions.assert_not_called()


    def test_iterator(self):
        x = LineGenerator("x", "mm", 1.0, 2.0, 5, False)
        y = LineGenerator("y", "mm", 1.0, 2.0, 5, False)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        points = list(g.iterator())
        expected_pos = [{"x":x/4., "y":y/4.}
            for y in range_(4, 9) for x in range_(4, 9)]
        self.assertEqual(expected_pos, [p.positions for p in points])
        expected_indexes = [[y, x] for y in range_(0, 5) for x in range_(0, 5)]
        self.assertEqual(expected_indexes, [p.indexes for p in points])


    def test_get_point(self):
        x = LineGenerator("x", "mm", -1., 1, 5, False)
        y = LineGenerator("y", "mm", -1., 1, 5, False)
        z = LineGenerator("z", "mm", -1., 1, 5, False)
        r = CircularROI([0., 0.], 1)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([z, y, x], [e], [])
        g.prepare()
        points = [g.get_point(n) for n in range(0, g.size)]
        pos = [p.positions for p in points]
        idx = [p.indexes for p in points]
        xy_expected = [(x/2., y/2.) for y in range_(-2, 3)
            for x in range_(-2, 3)]
        xy_expected = [(x, y) for (x, y) in xy_expected
            if x*x + y*y <= 1]
        expected = [{"x":x, "y":y, "z":z/2.} for z in range_(-2, 3)
            for (x, y) in xy_expected]
        self.assertEqual(expected, pos)
        expected_idx = [[z, xy] for z in range_(5)
            for xy in range_(len(xy_expected))]
        self.assertEqual(expected_idx, idx)


    def test_get_point_large_scan(self):
        s = SpiralGenerator(["x", "y"], "mm", [0, 0], 6, 1) #114 points
        z = LineGenerator("z", "mm", 0, 1, 100)
        w = LineGenerator("w", "mm", 0, 1, 5)
        t = LineGenerator("t", "mm", 0, 1, 5)
        rad1 = 2.8
        r1 = CircularROI([1., 1.], rad1)
        e1 = ROIExcluder([r1], ["x", "y"])
        rad2 = 2
        r2 = CircularROI([0.5, 0.5], rad2)
        e2 = ROIExcluder([r2], ["y", "z"])
        rad3 = 0.5
        r3 = CircularROI([0.5, 0.5], rad3)
        e3 = ROIExcluder([r3], ["w", "t"])
        g = CompoundGenerator([t, w, z, s], [e1, e2, e3], [])
        g.prepare()

        spiral = [(x, y) for (x, y) in zip(s.positions["x"], s.positions["y"])]
        zwt = [(z/99., w/4., t/4.) for t in range_(0, 5)
            for w in range_(0, 5)
            for z in range_(0, 100)]
        expected = [(x, y, z, w, t) for (z, w, t) in zwt for (x, y) in spiral]
        expected = [{"x":x, "y":y, "z":z, "w":w, "t":t}
                for (x,y,z,w,t) in expected if
                (x-1)*(x-1) + (y-1)*(y-1) <= rad1*rad1 and
                (y-0.5)*(y-0.5) + (z-0.5)*(z-0.5) <= rad2*rad2 and
                (w-0.5)*(w-0.5) + (t-0.5)*(t-0.5) <= rad3*rad3]
        points = [g.get_point(n) for n in range_(0, g.size)]
        pos = [p.positions for p in points]
        # assertEqual on a sequence of dicts is *really* slow
        for (e, p) in zip(expected, pos):
            self.assertEquals(e.keys(), p.keys())
            for k in e.keys():
                self.assertAlmostEqual(e[k], p[k])


    def test_alternating_simple(self):
        y = LineGenerator("y", "mm", 1, 5, 5)
        x = LineGenerator("x", "mm", 1, 5, 5, alternate=True)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        expected = []
        expected_idx = []
        expected_lower = []
        expected_upper = []
        for y in range_(1, 6):
            x_f = y % 2 == 1
            r = range_(1, 6) if x_f else range_(5, 0, -1)
            for x in r:
                expected.append({"y":float(y), "x":float(x)})
                expected_idx.append([y - 1, x - 1])
                expected_lower.append(x + (-0.5 if x_f else 0.5))
                expected_upper.append(x + (0.5 if x_f else -0.5))
        points = list(g.iterator())
        self.assertEqual(expected, [p.positions for p in points])
        self.assertEqual(expected_idx, [p.indexes for p in points])
        self.assertEqual(expected_lower, [p.lower["x"] for p in points])
        self.assertEqual(expected_upper, [p.upper["x"] for p in points])


    def test_alternating_three_axis(self):
        z = LineGenerator("z", "mm", 1, 2, 2)
        y = LineGenerator("y", "mm", 1, 2, 2, True)
        x = LineGenerator("x", "mm", 3, 1, 3, True)
        g = CompoundGenerator([z, y, x], [], [])
        g.prepare()
        expected = []
        expected_idx = []
        expected_lower = []
        expected_upper = []
        y_f = True
        x_f = True
        for z in range_(1, 3):
            y_r = range_(1, 3) if y_f else range_(2, 0, -1)
            y_f = not y_f
            for y in y_r:
                x_r = range_(3, 0, -1) if x_f else range_(1, 4)
                for x in x_r:
                    expected.append({"x":float(x), "y":float(y), "z":float(z)})
                    expected_idx.append([z-1, y-1, 3-x])
                    expected_lower.append(x + (0.5 if x_f else -0.5))
                    expected_upper.append(x + (-0.5 if x_f else 0.5))
                x_f = not x_f
        points = list(g.iterator())
        self.assertEqual(expected, [p.positions for p in points])
        self.assertEqual(expected_idx, [p.indexes for p in points])
        self.assertEqual(expected_lower, [p.lower["x"] for p in points])
        self.assertEqual(expected_upper, [p.upper["x"] for p in points])


    def test_alternating_with_region(self):
        y = LineGenerator("y", "mm", 1, 5, 5, True)
        x = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = CircularROI([3, 3], 1.5)
        e1 = ROIExcluder([r1], ["y", "x"])
        g = CompoundGenerator([y, x], [e1], [])
        g.prepare()
        expected = []
        x_f = True
        for y in range_(1, 6):
            r = range_(1, 6) if x_f else range(5, 0, -1)
            x_f = not x_f
            for x in r:
                expected.append({"y":float(y), "x":float(x)})
        expected = [p for p in expected if
            ((p["x"]-3)**2 + (p["y"]-3)**2 <= 1.5**2)]
        expected_idx = [[xy] for xy in range_(len(expected))]
        points = list(g.iterator())
        self.assertEqual(expected, [p.positions for p in points])
        self.assertEqual(expected_idx, [p.indexes for p in points])
        self.assertEqual((len(expected),), g.shape)


    def test_inner_alternating(self):
        z = LineGenerator("z", "mm", 1, 5, 5)
        y = LineGenerator("y", "mm", 1, 5, 5, alternate=True)
        x = LineGenerator("x", "mm", 1, 5, 5, alternate=True)
        r1 = CircularROI([3, 3], 1.5)
        e1 = ROIExcluder([r1], ["x", "y"])
        g = CompoundGenerator([z, y, x], [e1], [])
        g.prepare()
        expected = []
        xy_expected = []
        x_f = True
        for y in range_(1, 6):
            for x in (range_(1, 6) if x_f else range(5, 0, -1)):
                if (x-3)**2 + (y-3)**2 <= 1.5**2:
                    xy_expected.append((x, y))
            x_f = not x_f
        xy_f = True
        for z in range_(1, 6):
            for (x, y) in (xy_expected if xy_f else xy_expected[::-1]):
                expected.append({"x":float(x), "y":float(y), "z":float(z)})
            xy_f = not xy_f

        expected_idx = []
        xy_f = True
        for z in range_(0, 5):
            xy_idx = range_(len(xy_expected)) if xy_f \
                else range_(len(xy_expected)-1, -1, -1)
            expected_idx += [[z, xy] for xy in xy_idx]
            xy_f = not xy_f

        points = list(g.iterator())
        self.assertEqual(expected, [p.positions for p in points])
        self.assertEqual(expected_idx, [p.indexes for p in points])


    def test_two_dim_inner_alternates(self):
        wg = LineGenerator("w", "mm", 0, 1, 2)
        zg = LineGenerator("z", "mm", 0, 1, 2)
        yg = LineGenerator("y", "mm", 1, 3, 3, True)
        xg = LineGenerator("x", "mm", 0, 1, 2, True)
        r1 = EllipticalROI([0, 1], [1, 2])
        r2 = SectorROI([0, 0], [0.2, 1], [0, 7])
        e1 = ROIExcluder([r1], ['x', 'y'])
        e2 = ROIExcluder([r2], ['w', 'z'])
        g = CompoundGenerator([wg, zg, yg, xg], [e1, e2], [])
        g.prepare()
        actual = [p.positions for p in g.iterator()]
        expected = [(0, 1, 1, 0), (1, 1, 1, 0), (0, 2, 1, 0), (0, 3, 1, 0),
                (0, 3, 0, 1), (0, 2, 0, 1), (1, 1, 0, 1), (0, 1, 0, 1)]
        expected = [{"x":float(x), "y":float(y), "z":float(z), "w":float(w)}
            for (x, y, z, w) in expected]
        self.assertEqual(expected, actual)


    def test_three_dim_alternating_no_filter(self):
        zg = LineGenerator("z", "mm", 0, 2, 3, True)
        yg = LineGenerator("y", "mm", 0, 3, 4, True)
        xg = LineGenerator("x", "mm", 0, 2, 3, True)
        r1 = CircularROI([0, 0], 1000)
        e1 = ROIExcluder([r1], ["x", "y"])
        e2 = ROIExcluder([r1], ["x", "z"])
        g1 = CompoundGenerator([zg, yg, xg], [], [])
        g2 = CompoundGenerator([zg, yg, xg], [e1], [])
        g3 = CompoundGenerator([zg, yg, xg], [e2], [])
        g1.prepare()
        g2.prepare()
        g3.prepare()
        self.assertEquals((3, 4, 3), g1.shape)
        self.assertEquals((3, 12), g2.shape)
        self.assertEquals((36,), g3.shape)
        self.assertEqual(["z", "y", "x"], g1.axes)
        self.assertEqual(["z", "y", "x"], g2.axes)
        self.assertEqual(["z", "y", "x"], g3.axes)
        expected = [
                {'z':0, 'y':0, 'x':0}, {'z':0, 'y':0, 'x':1}, {'z':0, 'y':0, 'x':2},
                {'z':0, 'y':1, 'x':2}, {'z':0, 'y':1, 'x':1}, {'z':0, 'y':1, 'x':0},
                {'z':0, 'y':2, 'x':0}, {'z':0, 'y':2, 'x':1}, {'z':0, 'y':2, 'x':2},
                {'z':0, 'y':3, 'x':2}, {'z':0, 'y':3, 'x':1}, {'z':0, 'y':3, 'x':0},
                {'z':1, 'y':3, 'x':0}, {'z':1, 'y':3, 'x':1}, {'z':1, 'y':3, 'x':2},
                {'z':1, 'y':2, 'x':2}, {'z':1, 'y':2, 'x':1}, {'z':1, 'y':2, 'x':0},
                {'z':1, 'y':1, 'x':0}, {'z':1, 'y':1, 'x':1}, {'z':1, 'y':1, 'x':2},
                {'z':1, 'y':0, 'x':2}, {'z':1, 'y':0, 'x':1}, {'z':1, 'y':0, 'x':0},
                {'z':2, 'y':0, 'x':0}, {'z':2, 'y':0, 'x':1}, {'z':2, 'y':0, 'x':2},
                {'z':2, 'y':1, 'x':2}, {'z':2, 'y':1, 'x':1}, {'z':2, 'y':1, 'x':0},
                {'z':2, 'y':2, 'x':0}, {'z':2, 'y':2, 'x':1}, {'z':2, 'y':2, 'x':2},
                {'z':2, 'y':3, 'x':2}, {'z':2, 'y':3, 'x':1}, {'z':2, 'y':3, 'x':0},
                ]

        expected_lower_bounds = [
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                ]
        expected_upper_bounds = [
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                ]

        p1 = list(g1.iterator())
        p2 = list(g2.iterator())
        p3 = list(g3.iterator())
        self.assertEqual(len(expected), len(p1))
        self.assertEqual(len(expected), len(p2))
        self.assertEqual(len(expected), len(p3))
        for i, p in enumerate(p1):
            self.assertEqual(expected[i], p.positions)
        for i, p in enumerate(p2):
            self.assertEqual(expected[i], p.positions)
        for i, p in enumerate(p3):
            self.assertEqual(expected[i], p.positions)
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in p1])
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in p2])
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in p3])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in p1])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in p2])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in p3])


    def test_three_axis_alternating_filtered(self):
        zg = LineGenerator("z", "mm", 0, 2, 3, True)
        yg = LineGenerator("y", "mm", 0, 3, 4, True)
        xg = LineGenerator("x", "mm", 0, 2, 3, True)
        r = CircularROI([0, 0], 2.2)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([zg, yg, xg], [e], [])
        g.prepare()
        self.assertEqual((3, 6), g.shape)

        expected = [
                {'z':0, 'y':0, 'x':0}, {'z':0, 'y':0, 'x':1}, {'z':0, 'y':0, 'x':2},
                {'z':0, 'y':1, 'x':1}, {'z':0, 'y':1, 'x':0},
                {'z':0, 'y':2, 'x':0},
                {'z':1, 'y':2, 'x':0},
                {'z':1, 'y':1, 'x':0}, {'z':1, 'y':1, 'x':1},
                {'z':1, 'y':0, 'x':2}, {'z':1, 'y':0, 'x':1}, {'z':1, 'y':0, 'x':0},
                {'z':2, 'y':0, 'x':0}, {'z':2, 'y':0, 'x':1}, {'z':2, 'y':0, 'x':2},
                {'z':2, 'y':1, 'x':1}, {'z':2, 'y':1, 'x':0},
                {'z':2, 'y':2, 'x':0},
                ]

        expected_lower_bounds = [
                -0.5, 0.5, 1.5, 1.5, 0.5, -0.5,
                0.5, -0.5, 0.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 1.5, 0.5, -0.5,
                ]
        expected_upper_bounds = [
                0.5, 1.5, 2.5, 0.5, -0.5, 0.5,
                -0.5, 0.5, 1.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 0.5, -0.5, 0.5,
                ]

        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in points])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in points])


    def test_three_axis_alternating_outer_filtered(self):
        zg = LineGenerator("z", "mm", 0, 2, 3, True)
        yg = LineGenerator("y", "mm", 0, 3, 4, True)
        xg = LineGenerator("x", "mm", 0, 2, 3, True)
        r = CircularROI([0, 0], 2.2)
        e = ROIExcluder([r], ["y", "z"])
        g = CompoundGenerator([zg, yg, xg], [e], [])
        g.prepare()
        self.assertEqual((6, 3), g.shape)

        expected = [
                {'z':0, 'y':0, 'x':0}, {'z':0, 'y':0, 'x':1}, {'z':0, 'y':0, 'x':2},
                {'z':0, 'y':1, 'x':2}, {'z':0, 'y':1, 'x':1}, {'z':0, 'y':1, 'x':0},
                {'z':0, 'y':2, 'x':0}, {'z':0, 'y':2, 'x':1}, {'z':0, 'y':2, 'x':2},
                {'z':1, 'y':1, 'x':2}, {'z':1, 'y':1, 'x':1}, {'z':1, 'y':1, 'x':0},
                {'z':1, 'y':0, 'x':0}, {'z':1, 'y':0, 'x':1}, {'z':1, 'y':0, 'x':2},
                {'z':2, 'y':0, 'x':2}, {'z':2, 'y':0, 'x':1}, {'z':2, 'y':0, 'x':0},
                ]

        expected_lower_bounds = [
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5,
                ]

        expected_upper_bounds = [
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5,
                ]

        expected_indexes = [
                [0, 0], [0, 1], [0, 2], [1, 2], [1, 1], [1, 0],
                [2, 0], [2, 1], [2, 2], [3, 2], [3, 1], [3, 0],
                [4, 0], [4, 1], [4, 2], [5, 2], [5, 1], [5, 0],
                ]

        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in points])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in points])
        self.assertEqual(expected_indexes, [p.indexes for p in g.iterator()])


    def test_three_axis_alternating_all_filtered(self):
        z1g = LineGenerator("z1", "mm", 0, 2, 3, True)
        z2g = LineGenerator("z2", "mm", 0, 100, 2, True) # dummy axis to emulate 1D excluder
        yg = LineGenerator("y", "mm", 0, 3, 4, True)
        xg = LineGenerator("x", "mm", 0, 2, 3, True)
        r1 = CircularROI([0, 0], 2.8)
        r2 = CircularROI([2.5, 0], 1.5)
        e1 = ROIExcluder([r1], ["x", "y"])
        e2 = ROIExcluder([r2], ["z1", "z2"])
        g = CompoundGenerator([z2g, z1g, yg, xg], [e1, e2], [])
        g.prepare()
        self.assertEqual((2, 8), g.shape)

        expected = [
                {'z1':1, 'z2':0, 'x':0, 'y':0}, {'z1':1, 'z2':0, 'x':1, 'y':0},
                {'z1':1, 'z2':0, 'x':2, 'y':0}, {'z1':1, 'z2':0, 'x':2, 'y':1},
                {'z1':1, 'z2':0, 'x':1, 'y':1}, {'z1':1, 'z2':0, 'x':0, 'y':1},
                {'z1':1, 'z2':0, 'x':0, 'y':2}, {'z1':1, 'z2':0, 'x':1, 'y':2},
                {'z1':2, 'z2':0, 'x':1, 'y':2}, {'z1':2, 'z2':0, 'x':0, 'y':2},
                {'z1':2, 'z2':0, 'x':0, 'y':1}, {'z1':2, 'z2':0, 'x':1, 'y':1},
                {'z1':2, 'z2':0, 'x':2, 'y':1}, {'z1':2, 'z2':0, 'x':2, 'y':0},
                {'z1':2, 'z2':0, 'x':1, 'y':0}, {'z1':2, 'z2':0, 'x':0, 'y':0},
                ]

        expected_lower_bounds = [
                -0.5, 0.5, 1.5, 2.5, 1.5, 0.5, -0.5, 0.5,
                1.5, 0.5, -0.5, 0.5, 1.5, 2.5, 1.5, 0.5]

        expected_upper_bounds = [
                0.5, 1.5, 2.5, 1.5, 0.5, -0.5, 0.5, 1.5,
                0.5, -0.5, 0.5, 1.5, 2.5, 1.5, 0.5, -0.5]

        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)
        self.assertEqual(expected_lower_bounds, [p.lower["x"] for p in points])
        self.assertEqual(expected_upper_bounds, [p.upper["x"] for p in points])


    def test_three_dim_middle_alternates(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", -1, 3, 5, True)
        spiral = SpiralGenerator(["s1", "s2"], "mm", [1, 1], 2, 1, True)
        yg = LineGenerator("y", "mm", 0, 4, 5)
        xg = LineGenerator("x", "mm", 0, 4, 5)
        r1 = CircularROI([0, 0], 1)
        e1 = ROIExcluder([r1], ["s1", "z"])
        e2 = ROIExcluder([r1], ["y", "x"])
        g = CompoundGenerator([tg, zg, spiral, yg, xg], [e2, e1], [])
        g.prepare()

        it = 0
        iz = 0
        iy = 0
        ix = 0
        tzs = []
        points = []
        for t in range_(1, 6):
            for z in (range_(-1, 4) if it % 2 == 0 else range_(3, -2, -1)):
                s1p = spiral.positions["s1"] if iz % 2 == 0 else spiral.positions["s1"][::-1]
                s2p = spiral.positions["s2"] if iz % 2 == 0 else spiral.positions["s2"][::-1]
                points += [(x, y, s1, s2, z, t) for (s1, s2) in zip(s1p, s2p)
                        for y in range(0, 5) for x in range(0, 5)
                        if s1*s1 + z*z <= 1 and y*y + x*x <= 1]
                iz += 1
            it += 1
        expected = [{"x":float(x), "y":float(y), "s1":s1, "s2":s2, "z":float(z), "t":float(t)}
            for (x, y, s1, s2, z, t) in points]
        actual = [p.positions for p in list(g.iterator())]
        for e, a in zip(expected, actual):
            self.assertEqual(e, a)


    def test_triple_alternating_linked_gen(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", -1, 3, 5, True)
        yg = LineGenerator("y", "mm", 0, 4, 5, True)
        xg = LineGenerator("x", "mm", 0, 4, 5, True)
        r1 = RectangularROI([-1, -1], 5.5, 3.5)
        r2 = RectangularROI([1, 0], 2.5, 2.5)
        e1 = ROIExcluder([r1], ["z", "y"])
        e2 = ROIExcluder([r2], ["x", "y"])
        g = CompoundGenerator([tg, zg, yg, xg], [e1, e2], [])
        g.prepare()
        zf = True
        yf = True
        xf = True
        expected = []
        for t in range_(1, 6):
            zr = range_(-1, 4) if zf else range_(3, -2, -1)
            zf = not zf
            for z in zr:
                yr = range_(0, 5) if yf else range_(4, -1, -1)
                yf = not yf
                for y in yr:
                    xr = range_(0, 5) if xf else range_(4, -1, -1)
                    xf = not xf
                    for x in xr:
                       if z >= -1 and z < 4.5 and y >= 0 and y < 2.5 \
                            and x >= 1 and x < 3.5:
                            expected.append({"x":float(x), "y":float(y),
                                "z":float(z), "t":float(t)})
        actual = [p.positions for p in g.iterator()]
        self.assertEqual(len(expected), len(actual))
        for e, a in zip(expected, actual):
            self.assertEqual(e, a)


    def test_alternating_regions_2(self):
        z = LineGenerator("z", "mm", 1, 5, 5)
        y = LineGenerator("y", "mm", 1, 5, 5, True)
        x = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = CircularROI([3, 3], 1.5)
        e1 = ROIExcluder([r1], ["x", "y"])
        e2 = ROIExcluder([r1], ["z", "y"])
        g = CompoundGenerator([z, y, x], [e1, e2], []) #20 points
        g.prepare()
        actual = [p.positions for p in list(g.iterator())]
        expected = []
        yf = True
        xf = True
        for z in range_(1, 6):
            yr = range_(1, 6) if yf else range_(5, 0, -1)
            yf = not yf
            for y in yr:
                xr = range_(1, 6) if xf else range_(5, 0, -1)
                xf = not xf
                for x in xr:
                    expected.append({"x":float(x), "y":float(y), "z":float(z)})

        expected = [p for p in expected
            if (p["x"]-3)**2 + (p["y"]-3)**2 <= 1.5**2
            and (p["z"]-3)**2 + (p["y"]-3)**2 <= 1.5**2]
        self.assertEqual(expected, actual)


    def test_alternating_complex(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", 1, 5, 5, True)
        yg = LineGenerator("y", "mm", 1, 5, 5, True)
        xg = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = RectangularROI([3., 3.], 2., 2.)
        e1 = ROIExcluder([r1], ["y", "x"])
        e2 = ROIExcluder([r1], ["z", "y"])
        g = CompoundGenerator([tg, zg, yg, xg], [e1, e2], [])
        g.debug = True
        g.prepare()
        points = [p.positions for p in list(g.iterator())]
        expected = []
        zf, yf, xf = True, True, True
        for t in range_(1, 6):
            r_1 = range_(1,6) if zf else range_(5, 0, -1)
            zf = not zf
            for z in r_1:
                r_2 = range_(1,6) if yf else range_(5, 0, -1)
                yf = not yf
                for y in r_2:
                    r_3 = range_(1, 6) if xf else range_(5, 0, -1)
                    xf = not xf
                    for x in r_3:
                        expected.append(
                            {"t":float(t), "z":float(z),
                            "y":float(y), "x":float(x)})
        expected = [p for p in expected if
            (p["y"] >= 3 and p["y"] <= 5 and p["x"] >= 3 and p["x"] <= 5) and
            (p["z"] >= 3 and p["z"] <= 5 and p["y"] >= 3 and p["y"] <= 5)]
        self.assertEqual(expected, points)


    def test_mixed_alternating_simple(self):
        zg = LineGenerator("z", "mm", 1, 5, 5)
        yg = LineGenerator("y", "mm", 1, 5, 5)
        xg = LineGenerator("x", "mm", 1, 5, 5, True)
        e = SquashingExcluder(["x", "y"])
        g = CompoundGenerator([zg, yg, xg], [e], [])
        g.prepare()
        expected = []
        expected_idx = []
        expected_dim_x = [
                1, 2, 3, 4, 5,
                5, 4, 3, 2, 1,
                1, 2, 3, 4, 5,
                5, 4, 3, 2, 1,
                1, 2, 3, 4, 5]
        expected_dim_y = [
                1, 1, 1, 1, 1,
                2, 2, 2, 2, 2,
                3, 3, 3, 3, 3,
                4, 4, 4, 4, 4,
                5, 5, 5, 5, 5]
        for n1, z in enumerate(range_(1, 6)):
            for n2, (x, y) in enumerate(zip(expected_dim_x, expected_dim_y)):
                expected.append({"z":float(z), "y":float(y), "x":float(x)})
                expected_idx.append([n1, n2])
        points = [p.positions for p in list(g.iterator())]
        self.assertEqual(expected, points)
        self.assertEqual(expected_idx, [p.indexes for p in list(g.iterator())])


    def test_mixed_dim_complex(self):
        tg = LineGenerator("t", "mm", 1, 5, 5, False)
        zg = LineGenerator("z", "mm", 11, 13, 3, True)
        yg = LineGenerator("y", "mm", 21, 23, 3, True)
        xg = LineGenerator("x", "mm", 31, 33, 3, False)
        wg = LineGenerator("w", "mm", 41, 43, 3, True)
        m1 = np.array([0, 0, 1, 1, 0, 1, 1, 1, 0])
        m2 = np.array([1, 1, 0, 1, 1, 0, 1, 0, 1])
        e1 = MagicMock(spec=Excluder([]), axes=["x", "w"])
        e2 = MagicMock(spec=Excluder([]), axes=["z", "y"])
        e1.create_mask.return_value=m1
        e2.create_mask.return_value=m2
        i1, i2 = np.nonzero(m1)[0], np.nonzero(m2)[0]

        g = CompoundGenerator([tg, zg, yg, xg, wg], [e1, e2], [])
        g.prepare()
        d1_w = np.array([41, 42, 43, 43, 42, 41, 41, 42, 43])[i1]
        d1_x = np.array([31, 31, 31, 32, 32, 32, 33, 33, 33])[i1]
        d2_y = np.array([21, 22, 23, 23, 22, 21, 21, 22, 23])[i2]
        d2_z = np.array([11, 11, 11, 12, 12, 12, 13, 13, 13])[i2]

        expected = []
        expected_idx = []
        d2_y_alt = d2_y
        d2_z_alt = d2_z
        d2_idx = list(range_(len(d2_z)))
        d2_idx_alt = d2_idx

        for n1, t in enumerate(range_(1, 6)):
            for n2, y, z in zip(d2_idx_alt, d2_y_alt, d2_z_alt):
                for n3, (w, x) in enumerate(zip(d1_w, d1_x)):
                    expected.append({"t":float(t), "z":float(z), "y":float(y),
                        "x":float(x), "w":float(w)})
                    expected_idx.append([n1, n2, n3])
            d2_y_alt = d2_y_alt[::-1]
            d2_z_alt = d2_z_alt[::-1]
            d2_idx_alt = d2_idx_alt[::-1]
        points = [p.positions for p in list(g.iterator())]
        indexes = [p.indexes for p in list(g.iterator())]
        self.assertEqual(expected, points)
        self.assertEqual(expected_idx, indexes)


    def test_alternating_dim_inside_filtered(self):
        tg = LineGenerator("t", "mm", 1, 5, 5, False)
        zg = LineGenerator("z", "mm", 11, 13, 3, False)
        yg = LineGenerator("y", "mm", 21, 23, 3, True)
        xg = LineGenerator("x", "mm", 31, 33, 3, True)
        wg = LineGenerator("w", "mm", 41, 43, 3, True)
        m1 = np.array([0, 0, 1, 1, 0, 1, 1, 1, 0])
        m2 = np.array([1, 1, 0, 1, 1, 0, 1, 0, 1])
        e1 = MagicMock(spec=Excluder([]), axes=["x", "w"])
        e2 = MagicMock(spec=Excluder([]), axes=["z", "y"])
        e1.create_mask.return_value=m1
        e2.create_mask.return_value=m2
        i1, i2 = np.nonzero(m1)[0], np.nonzero(m2)[0]

        g = CompoundGenerator([tg, zg, yg, xg, wg], [e1, e2], [])
        g.prepare()
        d1_w = np.array([41, 42, 43, 43, 42, 41, 41, 42, 43])[i1]
        d1_x = np.array([31, 31, 31, 32, 32, 32, 33, 33, 33])[i1]
        d2_y = np.array([21, 22, 23, 23, 22, 21, 21, 22, 23])[i2]
        d2_z = np.array([11, 11, 11, 12, 12, 12, 13, 13, 13])[i2]
        d1_idx = list(range_(len(np.nonzero(m1)[0])))

        expected = []
        expected_idx = []

        d1_w_alt = d1_w
        d1_x_alt = d1_x
        d1_idx_alt = d1_idx
        m1_alt = m1

        for n1, t in enumerate(range_(1, 6)):
            n2 = 0
            for (y, z) in zip(d2_y, d2_z):
                idx_iter = iter(d1_idx_alt)
                for (w, x, m1v) in zip(d1_w_alt, d1_x_alt, m1_alt):
                    n3 = next(idx_iter)
                    expected.append({"t":float(t), "z":float(z), "y":float(y),
                        "x":float(x), "w":float(w)})
                    expected_idx.append([n1, n2, n3])
                n2 += 1
                d1_x_alt = d1_x_alt[::-1]
                d1_w_alt = d1_w_alt[::-1]
                d1_idx_alt = d1_idx_alt[::-1]

        points = [p.positions for p in list(g.iterator())]
        indexes = [p.indexes for p in list(g.iterator())]
        self.assertEqual(expected, points)
        self.assertEqual(expected_idx, indexes)


    def test_line_spiral(self):
        expected = [{'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 0.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 0.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 0.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 2.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 2.0},
                     {'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 2.0},
                     {'y': -0.3211855677650875, 'x': 0.23663214944574582, 'z': 4.0},
                     {'y': -0.25037538922751695, 'x': -0.6440318266552169, 'z': 4.0},
                     {'y': 0.6946549630820702, 'x': -0.5596688286164636, 'z': 4.0},
                     ]
        z = LineGenerator("z", "mm", 0.0, 4.0, 3)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 0.8, alternate=True)
        g = CompoundGenerator([z, spiral], [], [])
        g.prepare()
        self.assertEqual(g.axes, ["z", "x", "y"])
        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)


    def test_line_lissajous(self):
        expected = [{'y': 0.0, 'x': 0.5, 'z': 0.0},
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
        liss = LissajousGenerator(['x', 'y'], "mm", [0., 0.], [1., 1.], 1, size=5)
        g = CompoundGenerator([z, liss], [], [])
        g.prepare()
        self.assertEqual(g.axes, ["z", "x", "y"])
        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)


    def test_horrible_scan(self):
        lissajous = LissajousGenerator(
            ["j1", "j2"], "mm", [-0.5, 0.7], [2, 3.5], 7, 100)
        line2 = LineGenerator(["l2"], "mm", -3, 3, 7, True)
        line1 = LineGenerator(["l1"], "mm", -1, 2, 5, True)
        spiral = SpiralGenerator(["s1", "s2"], "mm", [1, 2], 5, 2.5, True)
        r1 = CircularROI([1, 1], 2)
        r2 = CircularROI([-1, -1], 4)
        r3 = CircularROI([1, 1], 2)
        e1 = ROIExcluder([r1], ["j1", "l2"])
        e2 = ROIExcluder([r2], ["s2", "l1"])
        e3 = ROIExcluder([r3], ["s1", "s2"])
        g = CompoundGenerator([lissajous, line2, line1, spiral], [e1, e2, e3], [])
        g.prepare()

        d1_s1 = np.append(spiral.positions["s1"], spiral.positions["s1"][::-1])
        d1_s1 = np.append(np.tile(d1_s1, 2), spiral.positions["s1"])
        d1_s2 = np.append(spiral.positions["s2"], spiral.positions["s2"][::-1])
        d1_s2 = np.append(np.tile(d1_s2, 2), spiral.positions["s2"])
        d1_l1 = np.repeat(line1.positions["l1"], len(spiral.positions["s1"]))
        d1_m = ((d1_s2+1)**2 + (d1_l1+1)**2 <= 16) & ((d1_s1-1)**2 + (d1_s2-1)**2 <= 4)
        d1_i = np.nonzero(d1_m)[0]

        d2_j1 = np.repeat(lissajous.positions["j1"], len(line2.positions["l2"]))
        d2_j2 = np.repeat(lissajous.positions["j2"], len(line2.positions["l2"]))
        d2_l2 = np.append(line2.positions["l2"], line2.positions["l2"][::-1])
        d2_l2 = np.tile(d2_l2, int(lissajous.size//2))
        d2_m = ((d2_j1-1)**2 + (d2_l2-1)**2) <= 4
        d2_i = np.nonzero(d2_m)[0]

        expected = []
        expected_idx = []

        d1_i_alt = d1_i
        n1_alt = list(range_(len(d1_i)))
        for n2, (j1, j2, l2) in enumerate(zip(d2_j1[d2_i], d2_j2[d2_i], d2_l2[d2_i])):
            for n1, s1, s2, l1 in zip(n1_alt, d1_s1[d1_i_alt], d1_s2[d1_i_alt], d1_l1[d1_i_alt]):
                expected.append({"j1":j1, "j2":j2, "l2":l2, "l1":l1, "s1":s1, "s2":s2})
                expected_idx.append([n2, n1])
            d1_i_alt = d1_i_alt[::-1]
            n1_alt = n1_alt[::-1]

        self.assertEqual((181, 10), g.shape)
        self.assertEqual(expected, [p.positions for p in g.iterator()])


    def test_double_spiral_scan(self):
        line1 = LineGenerator(["l1"], "mm", -1, 2, 5)
        spiral_s = SpiralGenerator(["s1", "s2"], "mm", [1, 2], 5, 2.5, True)
        spiral_t = SpiralGenerator(["t1", "t2"], "mm", [0, 0], 5, 2.5, True)
        line2 = LineGenerator(["l2"], "mm", -1, 2, 5, True)
        r = CircularROI([0, 0], 1)
        e1 = ROIExcluder([r], ["s1", "l1"])
        e2 = ROIExcluder([r], ["l2", "t1"])
        g = CompoundGenerator([line1, spiral_s, spiral_t, line2], [e1, e2], [])
        g.prepare()

        d1_s1 = np.append(spiral_s.positions["s1"], spiral_s.positions["s1"][::-1])
        d1_s1 = np.append(np.tile(d1_s1, 2), spiral_s.positions["s1"])
        d1_s2 = np.append(spiral_s.positions["s2"], spiral_s.positions["s2"][::-1])
        d1_s2 = np.append(np.tile(d1_s2, 2), spiral_s.positions["s2"])
        d1_l1 = np.repeat(line1.positions["l1"], spiral_s.size)
        d1_m = d1_s1*d1_s1 + d1_l1*d1_l1 <= 1
        d1_i = np.nonzero(d1_m)[0]

        d2_l2 = np.append(line2.positions["l2"], line2.positions["l2"][::-1])
        d2_l2_u = np.append(line2.bounds["l2"][1:], line2.bounds["l2"][:-1][::-1])
        d2_l2_l = np.append(line2.bounds["l2"][:-1], line2.bounds["l2"][1:][::-1])
        d2_l2 = np.tile(d2_l2, int(spiral_t.size // 2))
        d2_l2_u = np.tile(d2_l2_u, int(spiral_t.size // 2))
        d2_l2_l = np.tile(d2_l2_l, int(spiral_t.size // 2))
        if len(d2_l2) != spiral_t.size:
            d2_l2 = np.append(d2_l2, line2.positions["l2"])
            d2_l2_u = np.append(d2_l2_u, line2.bounds["l2"][1:])
            d2_l2_l = np.append(d2_l2_l, line2.bounds["l2"][:-1])
        d2_t1 = np.repeat(spiral_t.positions["t1"], line2.size)
        d2_t2 = np.repeat(spiral_t.positions["t2"], line2.size)
        d2_m = d2_l2*d2_l2 + d2_t1*d2_t1 <= 1
        d2_i = np.nonzero(d2_m)[0]

        expected = []
        expected_lower = []
        expected_upper = []
        expected_idx = []

        d2_i_alt = d2_i
        d2_l2_l_alt = d2_l2_l
        d2_l2_u_alt = d2_l2_u
        n2_alt = list(range(len(d2_i)))
        for n1, (l1, s1, s2) in enumerate(zip(d1_l1[d1_i], d1_s1[d1_i], d1_s2[d1_i])):
            for n2, t1, t2, l2, l2u, l2l in zip(
                    n2_alt, d2_t1[d2_i_alt], d2_t2[d2_i_alt],
                    d2_l2[d2_i_alt], d2_l2_u_alt[d2_i_alt], d2_l2_l_alt[d2_i_alt]):
                expected.append({"l1":l1, "s1":s1, "s2":s2, "t1":t1, "t2":t2, "l2":l2})
                expected_upper.append({"l1":l1, "s1":s1, "s2":s2, "t1":t1, "t2":t2, "l2":l2u})
                expected_lower.append({"l1":l1, "s1":s1, "s2":s2, "t1":t1, "t2":t2, "l2":l2l})
                expected_idx.append([n1, n2])
            d2_i_alt = d2_i_alt[::-1]
            n2_alt = n2_alt[::-1]
            d2_l2_l_alt, d2_l2_u_alt = d2_l2_u_alt, d2_l2_l_alt

        g_points = list(g.iterator())
        self.assertEqual(expected_lower, [p.lower for p in g_points])
        self.assertEqual(expected, [p.positions for p in g_points])
        self.assertEqual(expected_upper, [p.upper for p in g_points])
        self.assertEqual(expected_idx, [p.indexes for p in g_points])


    def test_mutators(self):
        mutator_1 = MagicMock(spec=Mutator)
        mutator_1.mutate = MagicMock(side_effect = lambda x,n:x)
        mutator_2 = RandomOffsetMutator(0, ["x"], {"x":1})
        mutator_2.calc_offset = MagicMock(return_value=0.1)
        x = LineGenerator('x', 'mm', 1, 5, 5)
        g = CompoundGenerator([x], [], [mutator_1, mutator_2], 0.2)
        g.prepare()
        x_pos = 1
        n = 0
        for p in g.iterator():
            self.assertEqual(0.2, p.duration)
            self.assertEqual({"x":x_pos + 0.1}, p.positions)
            mutator_1.mutate.assert_called_once_with(p, n)
            mutator_1.mutate.reset_mock()
            n += 1
            x_pos += 1
        self.assertEqual(6, x_pos)


    def test_grid_rect_region(self):
        xg = LineGenerator("x", "mm", 1, 10, 10)
        yg = LineGenerator("y", "mm", 1, 10, 10)
        r = RectangularROI([3, 3], 6, 6)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([yg, xg], [e], [])
        g.prepare()
        self.assertEqual(49, g.size)
        p = g.get_point(8)
        self.assertEqual([1, 1], p.indexes)
        self.assertEqual((4, 4), (p.positions['y'], p.positions['x']))
        p = g.get_point(48)
        self.assertEqual([6, 6], p.indexes)
        self.assertEqual((9, 9), (p.positions['y'], p.positions['x']))
        p = g.get_point(14)
        self.assertEqual([2, 0], p.indexes)
        self.assertEqual((5, 3), (p.positions['y'], p.positions['x']))


    def test_grid_double_rect_region_then_not_reduced(self):
        xg = LineGenerator("x", "mm", 1, 10, 10)
        yg = LineGenerator("y", "mm", 1, 10, 10)
        r1 = RectangularROI([3, 3], 6, 6)
        r2 = RectangularROI([3, 3], 6, 6)
        e = ROIExcluder([r1, r2], ["x", "y"])
        g = CompoundGenerator([yg, xg], [e], [])
        g.prepare()

        self.assertEqual(2, len(g.excluders[0].rois))


    def test_multi_roi_excluder(self):
        x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate=True)
        y = LineGenerator("y", "mm", 0.0, 3.0, 4)
        circles = ROIExcluder([CircularROI([1.0, 2.0], 2.0),
                               CircularROI([1.0, 2.0], 2.0)], ["x", "y"])
        expected_positions = [{'x': 1.0, 'y': 0.0},
                              {'x': 2.0, 'y': 1.0},
                              {'x': 1.0, 'y': 1.0},
                              {'x': 0.0, 'y': 1.0},
                              {'x': 0.0, 'y': 2.0},
                              {'x': 1.0, 'y': 2.0},
                              {'x': 2.0, 'y': 2.0},
                              {'x': 3.0, 'y': 2.0},
                              {'x': 2.0, 'y': 3.0},
                              {'x': 1.0, 'y': 3.0},
                              {'x': 0.0, 'y': 3.0}]

        g = CompoundGenerator([y, x], [circles], [])
        g.prepare()
        positions = [point.positions for point in list(g.iterator())]

        self.assertEqual(positions, expected_positions)


    def test_excluder_spread_axes(self):
        sp = SpiralGenerator(["s1", "s2"], ["mm", "mm"], centre=[0, 0], radius=1, scale=0.5, alternate=True)
        y = LineGenerator("y", "mm", 0, 1, 3, True)
        z = LineGenerator("z", "mm", -2, 3, 6, True)
        e = ROIExcluder([CircularROI([0., 0.], 1.0)], ["s1", "z"])
        g = CompoundGenerator([z, y, sp], [e], [])

        g.prepare()

        s1_pos, s2_pos = sp.positions["s1"], sp.positions["s2"]
        s1_pos = np.tile(np.append(s1_pos, s1_pos[::-1]), 9)
        s2_pos = np.tile(np.append(s2_pos, s2_pos[::-1]), 9)
        y_pos = np.tile(np.repeat(np.array([0, 0.5, 1.0, 1.0, 0.5, 0]), sp.size), 3)
        z_pos = np.repeat(np.array([-2, -1, 0, 1, 2, 3]), sp.size * 3)

        mask_func = lambda ps1, pz: ps1**2 + pz**2 <= 1
        mask = mask_func(s1_pos, z_pos)

        expected_s1 = s1_pos[mask]
        expected_s2 = s2_pos[mask]
        expected_y = y_pos[mask]
        expected_z = z_pos[mask]
        expected_positions = [{'s1':ps1, 's2':ps2, 'y':py, 'z':pz}
                for (ps1, ps2, py, pz) in zip(expected_s1, expected_s2, expected_y, expected_z)]
        positions = [point.positions for point in list(g.iterator())]

        self.assertEqual(positions, expected_positions)


    def test_bounds_applied_in_rectangle_roi_secial_case(self):
        x = LineGenerator("x", "mm", 0, 1, 2, True)
        y = LineGenerator("y", "mm", 0, 1, 2, True)
        r = RectangularROI([0, 0], 1, 1)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([y, x], [e], [])
        g.prepare()
        p = g.get_point(0)
        self.assertEqual({"x":-0.5, "y":0.}, p.lower)
        self.assertEqual({"x":0., "y":0.}, p.positions)
        self.assertEqual({"x":0.5, "y":0.}, p.upper)
        p = g.get_point(2)
        self.assertEqual({"x":1.5, "y":1}, p.lower)
        self.assertEqual({"x":1, "y":1}, p.positions)
        self.assertEqual({"x":0.5, "y":1}, p.upper)


    def test_no_bounds_for_non_continuous(self):
        x_points = np.array([1, 2])
        y_points = np.array([11, 12])
        x = MagicMock(axes=["x"], positions={"x":x_points}, size=len(x_points), alternate=False, spec=Generator)
        y = MagicMock(axes=["y"], positions={"y":y_points}, size=len(y_points), alternate=False, spec=Generator)

        g = CompoundGenerator([y, x], [], [], continuous=False)
        g.prepare()
        positions = [p.positions for p in g.iterator()]
        lower = [p.lower for p in g.iterator()]
        upper = [p.upper for p in g.iterator()]

        x.prepare_bounds.assert_not_called()
        y.prepare_bounds.assert_not_called()

        expected_positions = [{"x":1, "y":11}, {"x":2, "y":11},
                {"x":1, "y":12}, {"x":2, "y":12}]
        self.assertEqual(expected_positions, positions)
        self.assertEqual(expected_positions, lower)
        self.assertEqual(expected_positions, upper)


    def test_staticpointgen(self):
        m = StaticPointGenerator(3)
        g = CompoundGenerator([m], [], [])
        g.prepare()

        expected_positions = [{}] * 3
        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual([], g.axes)
        self.assertEqual({}, g.units)
        self.assertEqual(3, g.size)
        self.assertEqual((3,), g.shape)

        self.assertEqual(1, len(g.dimensions))
        self.assertEqual([], g.dimensions[0].upper)
        self.assertEqual([], g.dimensions[0].lower)
        self.assertEqual([], g.dimensions[0].axes)
        self.assertEqual(3, g.dimensions[0].size)


    def test_inner_staticpointgen(self):
        x = LineGenerator("x", "mm", 0, 1, 3, False)
        m = StaticPointGenerator(5)
        g = CompoundGenerator([x, m], [], [])
        g.prepare()

        expected_positions = [{'x':0.0}] * 5 + [{'x':0.5}] * 5 + [{'x':1.0}] * 5
        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(15, g.size)
        self.assertEqual((3, 5), g.shape)
        self.assertEqual(["x"], g.axes)
        self.assertEqual({"x":"mm"}, g.units)

        expected_dimensions = [{"axes":["x"], "size":3, "alternate":False, "upper":[1.0], "lower":[0.0]},
                {"axes":[], "size":5, "alternate":False, "upper":[], "lower":[]}]
        dimensions = [{"axes":d.axes, "size":d.size, "alternate":d.alternate, "upper":d.upper, "lower":d.lower}
                for d in g.dimensions]
        self.assertEqual(expected_dimensions, dimensions)


    def test_line_with_staticpointgen(self):
        x = LineGenerator("x", "mm", 0, 1, 3, False)
        m = StaticPointGenerator(5)
        g = CompoundGenerator([m, x], [], [])
        g.prepare()

        expected_positions = [{'x':0.0}, {'x':0.5}, {'x':1.0}] * 5
        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(15, g.size)
        self.assertEqual((5, 3), g.shape)
        self.assertEqual(["x"], g.axes)
        self.assertEqual({"x":"mm"}, g.units)

        expected_dimensions = [{"axes":[], "size":5, "alternate":False, "upper":[], "lower":[]},
                {"axes":["x"], "size":3, "alternate":False, "upper":[1.0], "lower":[0.0]}]
        dimensions = [{"axes":d.axes, "size":d.size, "alternate":d.alternate, "upper":d.upper, "lower":d.lower}
                for d in g.dimensions]
        self.assertEqual(expected_dimensions, dimensions)


    def test_alternating_line_with_staticpointgen(self):
        x = LineGenerator("x", "mm", 0, 1, 3, True)
        m = StaticPointGenerator(5)
        g = CompoundGenerator([m, x], [], [])
        g.prepare()
        expected_positions = [
                {'x':0.0}, {'x':0.5}, {'x':1.0},
                {'x':1.0}, {'x':0.5}, {'x':0.0},
                {'x':0.0}, {'x':0.5}, {'x':1.0},
                {'x':1.0}, {'x':0.5}, {'x':0.0},
                {'x':0.0}, {'x':0.5}, {'x':1.0}]

        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(15, g.size)
        self.assertEqual((5, 3), g.shape)
        self.assertEqual(["x"], g.axes)
        self.assertEqual({"x":"mm"}, g.units)

        expected_dimensions = [{"axes":[], "size":5, "alternate":False, "upper":[], "lower":[]},
                {"axes":["x"], "size":3, "alternate":True, "upper":[1.0], "lower":[0.0]}]
        dimensions = [{"axes":d.axes, "size":d.size, "alternate":d.alternate, "upper":d.upper, "lower":d.lower}
                for d in g.dimensions]
        self.assertEqual(expected_dimensions, dimensions)


    def test_intermediate_staticpointgen(self):
        x = LineGenerator("x", "mm", 0, 1, 3, False)
        y = LineGenerator("y", "cm", 2, 3, 4, False)
        m = StaticPointGenerator(5)
        g = CompoundGenerator([y, m, x], [], [])
        g.prepare()

        expected_positions = []
        for yp in [2.0, 2 + 1./3, 2 + 2./3, 3.0]:
            for mp in range_(5):
                for xp in [0.0, 0.5, 1.0]:
                    expected_positions.append({"y":yp, "x":xp})

        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(60, g.size)
        self.assertEqual((4, 5, 3), g.shape)
        self.assertEqual(["y", "x"], g.axes)
        self.assertEqual({"y":"cm", "x":"mm"}, g.units)
        self.assertEqual(3, len(g.dimensions))


    def test_staticpointgen_with_axis(self):
        x = LineGenerator("x", "mm", 0, 1, 3, False)
        y = LineGenerator("y", "cm", 2, 3, 4, False)
        m = StaticPointGenerator(5, "repeats")
        g = CompoundGenerator([y, x, m], [], [])
        g.prepare()

        expected_positions = []
        for yp in [2.0, 2 + 1./3, 2 + 2./3, 3.0]:
            for xp in [0.0, 0.5, 1.0]:
                for mp in range_(5):
                    expected_positions.append({"y": yp, "x": xp, "repeats": mp + 1})

        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(60, g.size)
        self.assertEqual((4, 3, 5), g.shape)
        self.assertEqual(["y", "x", "repeats"], g.axes)
        self.assertEqual({"y": "cm", "x": "mm", "repeats": ""}, g.units)


    def test_staticpointgen_with_axis_and_excluder(self):
        x = LineGenerator("x", "mm", 0, 1, 3, False)
        y = LineGenerator("y", "cm", 2, 3, 4, False)
        m = StaticPointGenerator(5, "repeats")
        e = SquashingExcluder(["x", "repeats"])
        g = CompoundGenerator([y, x, m], [e], [])
        g.prepare()

        # Expected positions should be the same as without the excluder
        expected_positions = []
        for yp in [2.0, 2 + 1./3, 2 + 2./3, 3.0]:
            for xp in [0.0, 0.5, 1.0]:
                for mp in range_(5):
                    expected_positions.append({"y": yp, "x": xp, "repeats": mp + 1})

        positions = [point.positions for point in g.iterator()]
        self.assertEqual(expected_positions, positions)

        self.assertEqual(60, g.size)
        self.assertEqual((4, 15), g.shape)
        self.assertEqual(["y", "x", "repeats"], g.axes)
        self.assertEqual({"y": "cm", "x": "mm", "repeats": ""}, g.units)
        self.assertEqual(2, len(g.dimensions))


    def test_staticpointgen_in_alternating(self):
        x = LineGenerator("x", "mm", 0, 1, 3, True)
        y = LineGenerator("y", "cm", 2, 3, 4, False)
        m = StaticPointGenerator(5)
        r = CircularROI((0.5, 2.5), 0.4)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([y, m, x], [e], [])
        g.prepare()

        expected_positions = []
        x_positions = [0.0, 0.5, 1.0]
        direction = 1
        for yp in [2.0, 2 + 1./3, 2 + 2./3, 3.0]:
            for mp in range_(5):
                for xp in x_positions[::direction]:
                    if (xp-0.5)**2 + (yp-2.5)**2 <= 0.4**2:
                        expected_positions.append({"y":yp, "x":xp})
                direction *= -1

        positions = [point.positions for point in g.iterator()]

        self.assertEqual(expected_positions, positions)
        self.assertEqual(len(expected_positions), g.size)
        self.assertEqual((len(expected_positions),), g.shape)
        self.assertEqual(["y", "x"], g.axes)
        self.assertEqual({"y":"cm", "x":"mm"}, g.units)
        self.assertEqual(1, len(g.dimensions))


    def test_delay_after(self):
        x = LineGenerator("x", "mm", 0, 1, 1)

        g = CompoundGenerator([x], [], [], duration=1, delay_after=2)
        g.prepare()

        delays = [point.delay_after for point in g.iterator()]
        self.assertEqual([2], delays)

    def test_negative_delay_after(self):
        x = LineGenerator("x", "mm", 0, 1, 1)

        g = CompoundGenerator([x], [], [], duration=1, delay_after=-1)
        g.prepare()

        delays = [point.delay_after for point in g.iterator()]
        self.assertEqual([0], delays)


class CompoundGeneratorInternalDataTests(ScanPointGeneratorTest):
    """Tests on datastructures internal to CompoundGenerator"""

    def test_post_prepare(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        self.assertEqual(g.size, 6)

        self.assertEqual(2, len(g.dimensions))
        dim_0 = g.dimensions[0]
        dim_1 = g.dimensions[1]
        self.assertEqual(["y"], dim_0.axes)
        self.assertEqual([True] * 2, dim_0.mask.tolist())
        self.assertEqual(["x"], dim_1.axes)
        self.assertEqual([True] * 3, dim_1.mask.tolist())
        self.assertEqual((2, 3), g.shape)

    def test_prepare_with_regions(self):
        x = LineGenerator("x", "mm", 0, 1, 5, False)
        y = LineGenerator("y", "mm", 0, 1, 5, False)
        circle = CircularROI([0., 0.], 1)
        excluder = ROIExcluder([circle], ['x', 'y'])
        g = CompoundGenerator([y, x], [excluder], [])
        g.prepare()
        self.assertEqual(1, len(g.dimensions))
        self.assertEqual(["y", "x"], g.dimensions[0].axes)
        expected_mask = [(x/4.)**2 + (y/4.)**2 <= 1
            for y in range(0, 5) for x in range(0, 5)]
        self.assertEqual(expected_mask, g.dimensions[0].mask.tolist())
        self.assertEqual((len([v for v in expected_mask if v]),), g.shape)

    def test_simple_mask(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, False)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, False)
        r = CircularROI([0, 0], 1)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([y, x], [e], [])
        g.prepare()
        p = [(x/2., y/2.) for y in range_(-2, 3) for x in range_(-2, 3)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[0].mask.tolist())

    def test_simple_mask_alternating(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, alternate=True)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, alternate=True)
        r = CircularROI([0.5, 0], 1)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([y, x], [e], [])
        g.prepare()
        reverse = False
        p = []
        for y in range_(-2, 3):
            if reverse:
                p += [(x/2., y/2.) for x in range_(2, -3, -1)]
            else:
                p += [(x/2., y/2.) for x in range_(-2, 3)]
            reverse = not reverse
        expected_mask = [(x-0.5)**2 + y**2 <= 1**2 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[0].mask.tolist())

    def test_double_mask_alternating_spiral(self):
        zgen = LineGenerator("z", "mm", 0.0, 4.0, 5, alternate=True)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3, alternate=True) #29 points
        r1 = RectangularROI([-2, -2], 4, 3)
        r2 = RectangularROI([-2, 0], 4, 3)
        e1 = ROIExcluder([r1], ["y", "x"])
        e2 = ROIExcluder([r2], ["y", "z"])
        g = CompoundGenerator([zgen, spiral], [e1, e2], [])
        g.prepare()
        xy = list(zip(spiral.positions['x'], spiral.positions['y']))
        p = []
        for z in range_(0, 5):
            p += [(x, y, z) for (x, y) in (xy if z % 2 == 0 else xy[::-1])]
        expected = [x >= -2 and x <= 1 and y >= -2 and y <= 2
                and z >= 0 and z <= 3 for (x, y, z) in p]
        actual = g.dimensions[0].mask.tolist()
        self.assertEqual(expected, actual)

    def test_double_mask_spiral(self):
        zgen = LineGenerator("z", "mm", 0.0, 4.0, 5)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3) #29 points
        r1 = RectangularROI([-2, -2], 4, 3)
        r2 = RectangularROI([-2, 0], 4, 3)
        e1 = ROIExcluder([r1], ["y", "x"])
        e2 = ROIExcluder([r2], ["y", "z"])
        g = CompoundGenerator([zgen, spiral], [e1, e2], [])
        g.prepare()
        p = list(zip(spiral.positions['x'], spiral.positions['y']))
        p = [(x, y, z) for z in range_(0, 5) for (x, y) in p]
        expected = [x >= -2 and x <= 1 and y >= -2 and y <= 2
                and z >= 0 and z <= 3 for (x, y, z) in p]
        actual = g.dimensions[0].mask.tolist()
        self.assertEqual(expected, actual)

    def test_simple_mask_alternating_spiral(self):
        z = LineGenerator("z", "mm", 0.0, 4.0, 5)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3, alternate=True) #29 points
        r = RectangularROI([-2, -2], 3, 4)
        e = ROIExcluder([r], ["x", "y"])
        g = CompoundGenerator([z, spiral], [e], [])
        g.prepare()
        p = list(zip(spiral.positions['x'], spiral.positions['y']))
        expected = [x >= -2 and x < 1 and y >= -2 and y < 2 for (x, y) in p]
        expected_r = [x >= -2 and x < 1 and y >= -2 and y < 2 for (x, y) in p[::-1]]
        actual = g.dimensions[1].mask.tolist()
        self.assertEqual(expected, actual)

    def test_double_mask(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, False)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, False)
        z = LineGenerator("z", "mm", -1.0, 1.0, 5, False)
        r = CircularROI([0.1, 0.2], 1)
        e1 = ROIExcluder([r], ["x", "y"])
        e2 = ROIExcluder([r], ["y", "z"])
        g = CompoundGenerator([z, y, x], [e1, e2], [])
        g.prepare()
        p = [(x/2., y/2., z/2.) for z in range_(-2, 3)
            for y in range_(-2, 3)
            for x in range_(-2, 3)]
        m1 = [(x-0.1)**2 + (y-0.2)**2 <= 1 for (x, y, z) in p]
        m2 = [(y-0.1)**2 + (z-0.2)**2 <= 1 for (x, y, z) in p]
        expected_mask = [(b1 and b2) for (b1, b2) in zip(m1, m2)]
        self.assertEqual(expected_mask, g.dimensions[0].mask.tolist())

    def test_complex_masks(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", 0, 4, 5, alternate=True)
        yg = LineGenerator("y", "mm", 1, 5, 5, alternate=True)
        xg = LineGenerator("x", "mm", 2, 6, 5, alternate=True)
        r1 = CircularROI([4., 4.], 1.5)
        e1 = ROIExcluder([r1], ["y", "x"])
        e2 = ROIExcluder([r1], ["z", "y"])
        g = CompoundGenerator([tg, zg, yg, xg], [e1, e2], [])
        g.prepare()

        t_mask = [True] * 5
        iy = 0
        ix = 0
        xyz_mask = []
        xyz = []
        for z in range_(0, 5):
            for y in (range_(1, 6) if iy % 2 == 0 else range_(5, 0, -1)):
                for x in (range_(2, 7) if ix % 2 == 0 else range_(6, 1, -1)):
                    xyz_mask.append( (x-4)**2 + (y-4)**2 <= 1.5**2 \
                        and (y-4)**2 + (z-4)**2 <= 1.5**2)
                    xyz.append((x, y, z))
                    ix += 1
                iy += 1

        self.assertEqual(t_mask, g.dimensions[0].mask.tolist())
        self.assertEqual(xyz_mask, g.dimensions[1].mask.tolist())

    def test_separate_indexes(self):
        x1 = LineGenerator("x1", "mm", -1.0, 1.0, 5, False)
        y1 = LineGenerator("y1", "mm", -1.0, 1.0, 5, False)
        z1 = LineGenerator("z1", "mm", -1.0, 1.0, 5, False)
        x2 = LineGenerator("x2", "mm", -1.0, 1.0, 5, False)
        y2 = LineGenerator("y2", "mm", -1.0, 1.0, 5, False)
        x3 = LineGenerator("x3", "mm", 0, 1.0, 5, False)
        y3 = LineGenerator("y3", "mm", 0, 1.0, 5, False)
        r = CircularROI([0, 0], 1)
        e1 = ROIExcluder([r], ["x1", "y1"])
        e2 = ROIExcluder([r], ["y1", "z1"])
        e3 = ROIExcluder([r], ["x1", "y1"])
        e4 = ROIExcluder([r], ["x2", "y2"])
        e5 = ROIExcluder([r], ["x3", "y3"])
        g = CompoundGenerator(
                [x3, y3, y2, x2, z1, y1, x1],
                [e1, e2, e3, e4, e5],
                [])
        g.prepare()
        p = [(x/2., y/2., z/2.) for z in range_(-2, 3)
            for y in range_(-2, 3)
            for x in range_(-2, 3)]
        m1 = [x*x + y*y <= 1 for (x, y, z) in p]
        m2 = [y*y + z*z <= 1 for (x, y, z) in p]
        expected_mask = [(b1 and b2) for (b1, b2) in zip(m1, m2)]
        self.assertEqual(expected_mask, g.dimensions[2].mask.tolist())
        p = [(x/2., y/2.) for y in range_(-2, 3) for x in range_(-2, 3)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[1].mask.tolist())
        p = [(x/4., y/4.) for y in range_(0, 5) for x in range_(0, 5)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[0].mask.tolist())


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.l1 = MagicMock(spec=Generator)
        self.l1.name = ['x']
        self.l1.axes = ['x']
        self.l1_dict = MagicMock()

        self.l2 = MagicMock(spec=Generator)
        self.l2.name = ['y']
        self.l2.axes = ['y']
        self.l2_dict = MagicMock()

        self.m1 = MagicMock(spec=Mutator)
        self.m1_dict = MagicMock()

        self.e1 = MagicMock(spec=Excluder)
        self.e1.name = "e1"
        self.e1_dict = MagicMock()

    def test_to_dict(self):
        self.g = CompoundGenerator([self.l2, self.l1], [self.e1], [self.m1], -1, True)

        self.l1.to_dict.return_value = self.l1_dict
        self.l2.to_dict.return_value = self.l2_dict
        self.e1.to_dict.return_value = self.e1_dict
        self.m1.to_dict.return_value = self.m1_dict

        gen_list = [self.l2_dict, self.l1_dict]
        mutators_list = [self.m1_dict]
        excluders_list = [self.e1_dict]

        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/CompoundGenerator:1.0"
        expected_dict['generators'] = gen_list
        expected_dict['excluders'] = excluders_list
        expected_dict['mutators'] = mutators_list
        expected_dict['duration'] = -1
        expected_dict['continuous'] = True
        expected_dict['delay_after'] = 0

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self): # todo Should test the delay_after here?

        g1 = LineGenerator("x1", "mm", -1.0, 1.0, 5, False)
        g1_dict = g1.to_dict()
        g2 = LineGenerator("y1", "mm", -1.0, 1.0, 5, False)
        g2_dict = g2.to_dict()

        r = CircularROI([0, 0], 1)
        excl_1 = ROIExcluder([r], ["x1", "y1"])
        excl1_1_dict = excl_1.to_dict()

        mutator_1 = RandomOffsetMutator(0, ["x"], {"x": 1})
        mutator_1_dict = mutator_1.to_dict()

        _dict = dict()
        _dict['generators'] = [g1_dict, g2_dict]
        _dict['excluders'] = [excl1_1_dict]
        _dict['mutators'] = [mutator_1_dict]
        _dict['duration'] = 12
        _dict['continuous'] = False

        units_dict = dict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = CompoundGenerator.from_dict(_dict)

        self.assertEqual(gen.generators[0].to_dict(), g1.to_dict())
        self.assertEqual(gen.generators[1].to_dict(), g2.to_dict())
        self.assertEqual(gen.mutators[0].to_dict(), mutator_1.to_dict())
        self.assertEqual(gen.excluders[0].to_dict(), excl_1.to_dict())
        self.assertEqual(gen.duration, 12)
        self.assertEqual(gen.continuous, False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
