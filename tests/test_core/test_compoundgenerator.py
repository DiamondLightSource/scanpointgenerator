import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator import SpiralGenerator
from scanpointgenerator import LissajousGenerator
from scanpointgenerator import ROIExcluder
from scanpointgenerator.rois import CircularROI, RectangularROI, EllipticalROI, SectorROI
from scanpointgenerator.mutators import RandomOffsetMutator
from scanpointgenerator.compat import range_

from pkg_resources import require
require("mock")
from mock import patch, MagicMock, ANY


class CompoundGeneratorTest(ScanPointGeneratorTest):
    def test_init(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        g = CompoundGenerator([y, x], [], [], 0.2)
        self.assertEqual(g.generators[0], y)
        self.assertEqual(g.generators[1], x)
        self.assertEqual(g.units, dict(y="mm", x="mm"))
        self.assertEqual(g.axes, ["y", "x"])
        self.assertEqual(g.duration, 0.2)

    def test_default_duration(self):
        g = CompoundGenerator([MagicMock()], [], [])
        self.assertEqual(-1, g.duration)

    def test_given_compound_raise_error(self):
        g = CompoundGenerator([], [], [])
        with self.assertRaises(TypeError):
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
        expected = [(0, 3, 1, 0), (0, 2, 1, 0), (1, 1, 1, 0), (0, 1, 1, 0),
            (0, 1, 0, 1), (1, 1, 0, 1), (0, 2, 0, 1), (0, 3, 0, 1)]
        expected = [{"x":float(x), "y":float(y), "z":float(z), "w":float(w)}
            for (x, y, z, w) in expected]
        self.assertEqual(expected, actual)

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

        l2_f = True
        l1_f = True
        s_f = True
        points = []
        for (j1, j2) in zip(lissajous.positions["j1"], lissajous.positions["j2"]):
            l2p = line2.positions["l2"] if l2_f else line2.positions["l2"][::-1]
            l2_f = not l2_f
            for l2 in l2p:
                l1p = line1.positions["l1"] if l1_f else line1.positions["l1"][::-1]
                l1_f = not l1_f
                for l1 in l1p:
                    sp = zip(spiral.positions["s1"], spiral.positions["s2"]) if s_f \
                        else zip(spiral.positions["s1"][::-1], spiral.positions["s2"][::-1])
                    s_f = not s_f
                    for (s1, s2) in sp:
                        points.append((s1, s2, l1, l2, j1, j2))

        self.assertEqual(lissajous.size * line2.size * line1.size * spiral.size, len(points))
        points = [(s1, s2, l1, l2, j1, j2) for (s1, s2, l1, l2, j1, j2) in points if
            (j1-1)**2 + (l2-1)**2 <= 4 and
            (s2+1)**2 + (l1+1)**2 <= 16 and
            (s1-1)**2 + (s2-1)**2 <= 4]
        self.assertEqual(len(points), g.size)
        generated_points = list(g.iterator())
        self.assertEqual(len(points), len(generated_points))

        actual = [p.positions for p in generated_points]
        expected = [{"j1":j1, "j2":j2, "l2":l2, "l1":l1, "s1":s1, "s2":s2}
            for (s1, s2, l1, l2, j1, j2) in points]
        for e, a in zip(expected, actual):
            self.assertEqual(e, a)
        self.assertEqual((181, 10), g.shape)

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

        points = []
        l1s = []
        tl2 = []

        s_f = True
        for l1 in line1.positions["l1"]:
            sp = zip(spiral_s.positions['s1'], spiral_s.positions['s2'])
            sp = sp if s_f else list(sp)[::-1]
            s_f = not s_f
            l1s += [(s1, s2, l1) for (s1, s2) in sp]
        l2_f = True
        for (t1, t2) in zip(spiral_t.positions['t1'], spiral_t.positions['t2']):
            l2p = line2.positions['l2'] if l2_f else line2.positions['l2'][::-1]
            l2pu = line2.bounds['l2'][1:len(line2.positions['l2'])+1]
            l2pl = line2.bounds['l2'][0:len(line2.positions['l2'])]
            if not l2_f:
                l2pu, l2pl = l2pl[::-1], l2pu[::-1]
            l2_f = not l2_f
            tl2 += [(l2, l2u, l2l, t1, t2) for (l2, l2u, l2l) in
                zip(l2p, l2pu, l2pl) if l2*l2 + t1*t1 <= 1]
        t_f = True
        for (s1, s2, l1) in l1s:
            inner = tl2 if t_f else tl2[::-1]
            t_f = not t_f
            points += [(l2, l2u, l2l, t1, t2, s1, s2, l1)
                for (l2, l2u, l2l, t1, t2) in inner if s1*s1 + l1*l1 <= 1]
        l1s_original = l1s
        l1s = [(s1, s2, l1) for (s1, s2, l1) in l1s if s1*s1 + l1*l1 <= 1]

        expected = [{"l2":l2, "t1":t1, "t2":t2, "s1":s1, "s2":s2, "l1":l1}
            for (l2, l2u, l2l, t1, t2, s1, s2, l1) in points]

        expected_idx = []
        t_f = (l1s_original.index(l1s[0])) % 2 == 0 # t_f is False
        for d1 in range_(len(l1s)):
            expected_idx += [[d1, d2] for d2 in (range_(len(tl2)) if t_f else
                range_(len(tl2) - 1, -1, -1))]
            t_f = not t_f

        expected_l2_lower = [l2l for (l2, l2u, l2l, t1, t2, s1, s2, l1) in points]
        expected_l2_upper = [l2u for (l2, l2u, l2l, t1, t2, s1, s2, l1) in points]

        gpoints = list(g.iterator())
        self.assertEqual(expected, [p.positions for p in gpoints])
        self.assertEqual(expected_idx, [p.indexes for p in gpoints])
        self.assertEqual(expected_l2_lower, [p.lower["l2"] for p in gpoints])
        self.assertEqual(expected_l2_upper, [p.upper["l2"] for p in gpoints])

    def test_mutators(self):
        mutator_1 = MagicMock()
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

    def test_to_dict(self):
        self.g = CompoundGenerator([self.l2, self.l1], [self.e1], [self.m1], -1)

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

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    @patch('scanpointgenerator.compoundgenerator.Mutator')
    @patch('scanpointgenerator.compoundgenerator.Excluder')
    @patch('scanpointgenerator.compoundgenerator.Generator')
    def test_from_dict(self, gen_mock, ex_mock, mutator_mock):
        self.g = CompoundGenerator([self.l2, self.l1], [self.e1], [self.m1])

        gen_mock.from_dict.side_effect = [self.l2, self.l1]
        mutator_mock.from_dict.return_value = self.m1
        ex_mock.from_dict.return_value = self.e1

        _dict = dict()
        _dict['generators'] = [self.l1_dict, self.l2_dict]
        _dict['excluders'] = [self.e1_dict]
        _dict['mutators'] = [self.m1_dict]
        _dict['duration'] = 12

        units_dict = dict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = CompoundGenerator.from_dict(_dict)

        self.assertEqual(gen.generators[0], self.l2)
        self.assertEqual(gen.generators[1], self.l1)
        self.assertEqual(gen.mutators[0], self.m1)
        self.assertEqual(gen.excluders[0], self.e1)
        self.assertEqual(gen.duration, 12)

if __name__ == "__main__":
    unittest.main(verbosity=2)
