import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator import SpiralGenerator
from scanpointgenerator import LissajousGenerator
from scanpointgenerator import Excluder
from scanpointgenerator.rois import CircularROI, RectangularROI, EllipticalROI, SectorROI
from scanpointgenerator.mutators import FixedDurationMutator, RandomOffsetMutator
from scanpointgenerator.compat import range_

from pkg_resources import require
require("mock")
from mock import patch, MagicMock, ANY


class CompoundGeneratorTest(ScanPointGeneratorTest):
    def test_init(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        g = CompoundGenerator([y, x], [], [])
        self.assertEqual(g.generators[0], y)
        self.assertEqual(g.generators[1], x)
        self.assertEqual(g.position_units, dict(y="mm", x="mm"))
        self.assertEqual(g.axes, ["y", "x"])

    def test_given_compound_raise_error(self):
        g = CompoundGenerator([], [], [])
        with self.assertRaises(TypeError):
            CompoundGenerator([g], [], [])

    def test_duplicate_name_raises(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("x", "mm", 2.0, 2.1, 2, False)
        with self.assertRaises(ValueError):
            CompoundGenerator([y, x], [], [])

    def test_iterator(self):
        x = LineGenerator("x", "mm", 1.0, 2.0, 5, False)
        y = LineGenerator("y", "mm", 1.0, 2.0, 5, False)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        points = list(g.iterator())
        expected_pos = [{"x":x/4., "y":y/4.}
            for y in range_(4, 9) for x in range_(4, 9)]
        self.assertEqual(expected_pos, [p.positions for p in points])

    def test_get_point(self):
        x = LineGenerator("x", "mm", -1., 1, 5, False)
        y = LineGenerator("y", "mm", -1., 1, 5, False)
        z = LineGenerator("z", "mm", -1., 1, 5, False)
        r = CircularROI([0., 0.], 1)
        e = Excluder(r, ["x", "y"])
        g = CompoundGenerator([z, y, x], [e], [])
        g.prepare()
        points = [g.get_point(n) for n in range(0, g.num)]
        pos = [p.positions for p in points]
        expected = [(x/2., y/2., z/2.) for z in range_(-2, 3)
            for y in range_(-2, 3)
            for x in range_(-2, 3)]
        expected = [{'x':x, 'y':y, 'z':z} for (x, y, z) in expected if x*x + y*y <= 1]
        self.assertEqual(expected, pos)

    def test_get_point_large_scan(self):
        s = SpiralGenerator(["x", "y"], "mm", [0, 0], 6, 1) #114 points
        z = LineGenerator("z", "mm", 0, 1, 100)
        w = LineGenerator("w", "mm", 0, 1, 5)
        t = LineGenerator("t", "mm", 0, 1, 5)
        rad1 = 2.8
        r1 = CircularROI([1., 1.], rad1)
        e1 = Excluder(r1, ["x", "y"])
        rad2 = 2
        r2 = CircularROI([0.5, 0.5], rad2)
        e2 = Excluder(r2, ["y", "z"])
        rad3 = 0.5
        r3 = CircularROI([0.5, 0.5], rad3)
        e3 = Excluder(r3, ["w", "t"])
        g = CompoundGenerator([t, w, z, s], [e1, e2, e3], [])
        g.prepare()

        spiral = [(x, y) for (x, y) in zip(s.points["x"], s.points["y"])]
        zwt = [(z/99., w/4., t/4.) for t in range_(0, 5)
            for w in range_(0, 5)
            for z in range_(0, 100)]
        expected = [(x, y, z, w, t) for (z, w, t) in zwt for (x, y) in spiral]
        expected = [{"x":x, "y":y, "z":z, "w":w, "t":t}
                for (x,y,z,w,t) in expected if
                (x-1)*(x-1) + (y-1)*(y-1) <= rad1*rad1 and
                (y-0.5)*(y-0.5) + (z-0.5)*(z-0.5) <= rad2*rad2 and
                (w-0.5)*(w-0.5) + (t-0.5)*(t-0.5) <= rad3*rad3]
        points = [g.get_point(n) for n in range_(0, g.num)]
        pos = [p.positions for p in points]
        # assertEqual on a sequence of dicts is *really* slow
        for (e, p) in zip(expected, pos):
            self.assertEquals(e.keys(), p.keys())
            for k in e.keys():
                self.assertAlmostEqual(e[k], p[k])

    def test_alternating_simple(self):
        y = LineGenerator("y", "mm", 1, 5, 5)
        x = LineGenerator("x", "mm", 1, 5, 5, alternate_direction=True)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        expected = []
        for y in range(1, 6):
            r = range(1, 6) if y % 2 == 1 else range(5, 0, -1)
            for x in r:
                expected.append({"y":float(y), "x":float(x)})
        points = [p.positions for p in list(g.iterator())]
        self.assertEqual(expected, points)

    def test_alternating_three_axis(self):
        z = LineGenerator("z", "mm", 1, 2, 2)
        y = LineGenerator("y", "mm", 1, 2, 2, True)
        x = LineGenerator("x", "mm", 1, 3, 3, True)
        g = CompoundGenerator([z, y, x], [], [])
        g.prepare()
        expected = []
        y_f = True
        x_f = True
        for z in range_(1, 3):
            y_r = range_(1, 3) if y_f else range_(2, 0, -1)
            y_f = not y_f
            for y in y_r:
                x_r = range_(1, 4) if x_f else range_(3, 0, -1)
                x_f = not x_f
                for x in x_r:
                    expected.append({"x":float(x), "y":float(y), "z":float(z)})
        actual = [p.positions for p in g.iterator()]
        self.assertEqual(expected, actual)

    def test_alternating_with_region(self):
        y = LineGenerator("y", "mm", 1, 5, 5, True)
        x = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = RectangularROI([2, 2], 2, 2)
        e1 = Excluder(r1, ["y", "x"])
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
            (p["y"] >= 2 and p["y"] < 4 and p["x"] >= 2 and p["x"] < 4)]
        points = [p.positions for p in list(g.iterator())]
        self.assertEqual(expected, points)

    def test_inner_alternating(self):
        z = LineGenerator("z", "mm", 1, 5, 5)
        y = LineGenerator("y", "mm", 1, 5, 5, alternate_direction=True)
        x = LineGenerator("x", "mm", 1, 5, 5, alternate_direction=True)
        r1 = RectangularROI([2, 2], 2, 2)
        e1 = Excluder(r1, ["x", "y"])
        g = CompoundGenerator([z, y, x], [e1], [])
        g.prepare()
        actual = [p.positions for p in list(g.iterator())]
        expected = []
        iy = 0
        ix = 0
        for z in range_(1, 6):
            for y in (range(1, 6) if iy % 2 == 0 else range(5, 0, -1)):
                for x in (range(1, 6) if ix % 2 == 0 else range(5, 0, -1)):
                    if x >= 2 and x < 4 and y >= 2 and y < 4:
                        expected.append(
                            {"x":float(x), "y":float(y), "z":float(z)})
                    ix += 1
                iy += 1
        self.assertEqual(expected, actual)

    def test_two_dim_inner_alternates(self):
        wg = LineGenerator("w", "mm", 0, 1, 2)
        zg = LineGenerator("z", "mm", 0, 1, 2)
        yg = LineGenerator("y", "mm", 1, 3, 3, True)
        xg = LineGenerator("x", "mm", 0, 1, 2, True)
        r1 = EllipticalROI([0, 1], [1, 2])
        r2 = SectorROI([0, 0], [0.2, 1], [0, 7])
        e1 = Excluder(r1, ['x', 'y'])
        e2 = Excluder(r2, ['w', 'z'])
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
        e1 = Excluder(r1, ["s1", "z"])
        e2 = Excluder(r1, ["y", "x"])
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
                s1p = spiral.points["s1"] if iz % 2 == 0 else spiral.points["s1"][::-1]
                s2p = spiral.points["s2"] if iz % 2 == 0 else spiral.points["s2"][::-1]
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
        e1 = Excluder(r1, ["z", "y"])
        e2 = Excluder(r2, ["x", "y"])
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
        z = LineGenerator("z", "mm", 1, 5, 5, True)
        y = LineGenerator("y", "mm", 1, 5, 5, True)
        x = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = RectangularROI([2, 2], 2, 2)
        e1 = Excluder(r1, ["x", "y"])
        e2 = Excluder(r1, ["z", "y"])
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
            if p["x"] >= 2 and p["x"] < 4 and p["y"] >= 2 and p["y"] < 4
            and p["z"] >= 2 and p["z"] < 4]
        self.assertEqual(expected, actual)

    def test_alternating_complex(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", 1, 5, 5, True)
        yg = LineGenerator("y", "mm", 1, 5, 5, True)
        xg = LineGenerator("x", "mm", 1, 5, 5, True)
        r1 = RectangularROI([3., 3.], 2., 2.)
        e1 = Excluder(r1, ["y", "x"])
        e2 = Excluder(r1, ["z", "y"])
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
            (p["y"] >= 3 and p["y"] < 5 and p["x"] >= 3 and p["x"] < 5) and
            (p["z"] >= 3 and p["z"] < 5 and p["y"] >= 3 and p["y"] < 5)]
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
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 0.8, alternate_direction=True)
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
        box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        liss = LissajousGenerator(['x', 'y'], "mm", box, 1, num_points=5)
        g = CompoundGenerator([z, liss], [], [])
        g.prepare()
        self.assertEqual(g.axes, ["z", "x", "y"])
        points = list(g.iterator())
        self.assertEqual(len(expected), len(points))
        for i, p in enumerate(points):
            self.assertEqual(expected[i], p.positions)

    def test_horrible_scan(self):
        lissajous = LissajousGenerator(
            ["j1", "j2"], "mm",
            {"centre":[-0.5, 0.7], "width":2, "height":3.5},
            7, 100, True)
        line2 = LineGenerator(["l2"], "mm", -3, 3, 7, True)
        line1 = LineGenerator(["l1"], "mm", -1, 2, 5, True)
        spiral = SpiralGenerator(["s1", "s2"], "mm", [1, 2], 5, 2.5, True)
        r1 = CircularROI([1, 1], 2)
        r2 = CircularROI([-1, -1], 4)
        r3 = CircularROI([1, 1], 1)
        e1 = Excluder(r1, ["j1", "l2"])
        e2 = Excluder(r2, ["s2", "l1"])
        e3 = Excluder(r3, ["s1", "s2"])
        g = CompoundGenerator([lissajous, line2, line1, spiral], [e1, e2, e3], [])
        g.prepare()

        l2_f = True
        l1_f = True
        s_f = True
        points = []
        for (j1, j2) in zip(lissajous.points["j1"], lissajous.points["j2"]):
            l2p = line2.points["l2"] if l2_f else line2.points["l2"][::-1]
            l2_f = not l2_f
            for l2 in l2p:
                l1p = line1.points["l1"] if l1_f else line1.points["l1"][::-1]
                l1_f = not l1_f
                for l1 in l1p:
                    sp = zip(spiral.points["s1"], spiral.points["s2"]) if s_f \
                        else zip(spiral.points["s1"][::-1], spiral.points["s2"][::-1])
                    s_f = not s_f
                    for (s1, s2) in sp:
                        points.append((s1, s2, l1, l2, j1, j2))

        self.assertEqual(lissajous.num * line2.num * line1.num * spiral.num, len(points))
        points = [(s1, s2, l1, l2, j1, j2) for (s1, s2, l1, l2, j1, j2) in points if
            (j1-1)**2 + (l2-1)**2 <= 4 and
            (s2+1)**2 + (l1+1)**2 <= 16 and
            (s1-1)**2 + (s2-1)**2 <= 1]
        self.assertEqual(len(points), g.num)
        generated_points = list(g.iterator())
        self.assertEqual(len(points), len(generated_points))

        actual = [p.positions for p in generated_points]
        expected = [{"j1":j1, "j2":j2, "l2":l2, "l1":l1, "s1":s1, "s2":s2}
            for (s1, s2, l1, l2, j1, j2) in points]
        for e, a in zip(expected, actual):
            self.assertEqual(e, a)

    def test_double_spiral_scan(self):
        line1 = LineGenerator(["l1"], "mm", -1, 2, 5, True)
        spiral_s = SpiralGenerator(["s1", "s2"], "mm", [1, 2], 5, 2.5, True)
        spiral_t = SpiralGenerator(["t1", "t2"], "mm", [0, 0], 5, 2.5, True)
        line2 = LineGenerator(["l2"], "mm", -1, 2, 5, True)
        r = CircularROI([0, 0], 1)
        e1 = Excluder(r, ["s1", "l1"])
        e2 = Excluder(r, ["l2", "t1"])
        g = CompoundGenerator([line1, spiral_s, spiral_t, line2], [e1, e2], [])
        g.prepare()

        points = []
        s_f = True
        t_f = True
        l2_f = True
        for l1 in line1.points["l1"]:
            sp = zip(spiral_s.points['s1'], spiral_s.points['s2'])
            sp = sp if s_f else list(sp)[::-1]
            s_f = not s_f
            for (s1, s2) in sp:
                tp = zip(spiral_t.points["t1"], spiral_t.points["t2"])
                tp = tp if t_f else list(tp)[::-1]
                t_f = not t_f
                for (t1, t2) in tp:
                    l2p = line2.points['l2'] if l2_f else line2.points['l2'][::-1]
                    l2_f = not l2_f
                    for l2 in l2p:
                        points.append((l2, t1, t2, s1, s2, l1))

        expected = [{"l2":l2, "t1":t1, "t2":t2, "s1":s1, "s2":s2, "l1":l1}
            for (l2, t1, t2, s1, s2, l1) in points if
            s1*s1 + l1*l1 <= 1 and l2*l2 + t1*t1 <= 1]

        actual = [p.positions for p in list(g.iterator())]
        self.assertEqual(expected, actual)

    def test_mutators(self):
        mutator_1 = FixedDurationMutator(0.2)
        mutator_2 = RandomOffsetMutator(0, ["x"], {"x":1})
        mutator_2.get_random_number = MagicMock(return_value=0.1)
        x = LineGenerator('x', 'mm', 1, 5, 5)
        g = CompoundGenerator([x], [], [mutator_1, mutator_2])
        g.prepare()
        x_pos = 1
        for p in g.iterator():
            self.assertEqual(0.2, p.duration)
            self.assertEqual({"x":x_pos + 0.1}, p.positions)
            x_pos += 1
        self.assertEqual(6, x_pos)

class CompoundGeneratorInternalDataTests(ScanPointGeneratorTest):
    """Tests on datastructures internal to CompoundGenerator"""

    def test_post_prepare(self):
        x = LineGenerator("x", "mm", 1.0, 1.2, 3, True)
        y = LineGenerator("y", "mm", 2.0, 2.1, 2, False)
        g = CompoundGenerator([y, x], [], [])
        g.prepare()
        self.assertListAlmostEqual([1.0, 1.1, 1.2], g.axes_points["x"].tolist())
        self.assertListAlmostEqual([0.95, 1.05, 1.15], g.axes_points_lower["x"].tolist())
        self.assertListAlmostEqual([1.05, 1.15, 1.25], g.axes_points_upper["x"].tolist())
        self.assertListAlmostEqual([2.0, 2.1], g.axes_points["y"].tolist())
        self.assertListAlmostEqual([1.95, 2.05], g.axes_points_lower["y"].tolist())
        self.assertListAlmostEqual([2.05, 2.15], g.axes_points_upper["y"].tolist())
        self.assertEqual(g.num, 6)

        self.assertEqual(2, len(g.dimensions))
        self.assertEqual(["y"], g.dimensions[0]["axes"])
        self.assertEqual([True] * 2, g.dimensions[0]["mask"].tolist())
        self.assertEqual(["x"], g.dimensions[1]["axes"])
        self.assertEqual([True] * 3, g.dimensions[1]["mask"].tolist())

    def test_prepare_with_regions(self):
        x = LineGenerator("x", "mm", 0, 1, 5, False)
        y = LineGenerator("y", "mm", 0, 1, 5, False)
        circle = CircularROI([0., 0.], 1)
        excluder = Excluder(circle, ['x', 'y'])
        g = CompoundGenerator([y, x], [excluder], [])
        g.prepare()
        self.assertEqual(1, len(g.dimensions))
        self.assertEqual(["y", "x"], g.dimensions[0]["axes"])
        expected_mask = [(x/4.)**2 + (y/4.)**2 <= 1
            for y in range(0, 5) for x in range(0, 5)]
        self.assertEqual(expected_mask, g.dimensions[0]["mask"].tolist())

    def test_simple_mask(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, False)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, False)
        r = CircularROI([0, 0], 1)
        e = Excluder(r, ["x", "y"])
        g = CompoundGenerator([y, x], [e], [])
        g.prepare()
        p = [(x/2., y/2.) for y in range_(-2, 3) for x in range_(-2, 3)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[0]["mask"].tolist())

    def test_simple_mask_alternating(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, alternate_direction=True)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, alternate_direction=True)
        r = CircularROI([0.5, 0], 1)
        e = Excluder(r, ["x", "y"])
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
        self.assertEqual(expected_mask, g.dimensions[0]["mask"].tolist())

    def test_double_mask_alternating_spiral(self):
        zgen = LineGenerator("z", "mm", 0.0, 4.0, 5, alternate_direction=True)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3, alternate_direction=True) #29 points
        r1 = RectangularROI([-2, -2], 4, 3)
        r2 = RectangularROI([-2, 0], 4, 3)
        e1 = Excluder(r1, ["y", "x"])
        e2 = Excluder(r2, ["y", "z"])
        g = CompoundGenerator([zgen, spiral], [e1, e2], [])
        g.prepare()
        xy = list(zip(g.axes_points['x'], g.axes_points['y']))
        p = []
        for z in range_(0, 5):
            p += [(x, y, z) for (x, y) in (xy if z % 2 == 0 else xy[::-1])]
        expected = [x >= -2 and x < 1 and y >= -2 and y < 2
                and z >= 0 and z < 3 for (x, y, z) in p]
        actual = g.dimensions[0]["mask"].tolist()
        self.assertEqual(expected, actual)

    def test_double_mask_spiral(self):
        zgen = LineGenerator("z", "mm", 0.0, 4.0, 5)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3) #29 points
        r1 = RectangularROI([-2, -2], 4, 3)
        r2 = RectangularROI([-2, 0], 4, 3)
        e1 = Excluder(r1, ["y", "x"])
        e2 = Excluder(r2, ["y", "z"])
        g = CompoundGenerator([zgen, spiral], [e1, e2], [])
        g.prepare()
        p = list(zip(g.axes_points['x'], g.axes_points['y']))
        p = [(x, y, z) for z in range_(0, 5) for (x, y) in p]
        expected = [x >= -2 and x < 1 and y >= -2 and y < 2
                and z >= 0 and z < 3 for (x, y, z) in p]
        actual = g.dimensions[0]["mask"].tolist()
        self.assertEqual(expected, actual)

    def test_simple_mask_alternating_spiral(self):
        z = LineGenerator("z", "mm", 0.0, 4.0, 5)
        spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 3, alternate_direction=True) #29 points
        r = RectangularROI([-2, -2], 3, 4)
        e = Excluder(r, ["x", "y"])
        g = CompoundGenerator([z, spiral], [e], [])
        g.prepare()
        p = list(zip(g.axes_points['x'], g.axes_points['y']))
        expected = [x >= -2 and x < 1 and y >= -2 and y < 2 for (x, y) in p]
        expected_r = [x >= -2 and x < 1 and y >= -2 and y < 2 for (x, y) in p[::-1]]
        actual = g.dimensions[1]["mask"].tolist()
        self.assertEqual(expected, actual)

    def test_double_mask(self):
        x = LineGenerator("x", "mm", -1.0, 1.0, 5, False)
        y = LineGenerator("y", "mm", -1.0, 1.0, 5, False)
        z = LineGenerator("z", "mm", -1.0, 1.0, 5, False)
        r = CircularROI([0.1, 0.2], 1)
        e1 = Excluder(r, ["x", "y"])
        e2 = Excluder(r, ["y", "z"])
        g = CompoundGenerator([z, y, x], [e1, e2], [])
        g.prepare()
        p = [(x/2., y/2., z/2.) for z in range_(-2, 3)
            for y in range_(-2, 3)
            for x in range_(-2, 3)]
        m1 = [(x-0.1)**2 + (y-0.2)**2 <= 1 for (x, y, z) in p]
        m2 = [(y-0.1)**2 + (z-0.2)**2 <= 1 for (x, y, z) in p]
        expected_mask = [(b1 and b2) for (b1, b2) in zip(m1, m2)]
        self.assertEqual(expected_mask, g.dimensions[0]["mask"].tolist())

    def test_complex_masks(self):
        tg = LineGenerator("t", "mm", 1, 5, 5)
        zg = LineGenerator("z", "mm", 0, 4, 5, alternate_direction=True)
        yg = LineGenerator("y", "mm", 1, 5, 5, alternate_direction=True)
        xg = LineGenerator("x", "mm", 2, 6, 5, alternate_direction=True)
        r1 = RectangularROI([3., 3.], 2., 2.)
        e1 = Excluder(r1, ["y", "x"])
        e2 = Excluder(r1, ["z", "y"])
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
                    xyz_mask.append( x >= 3 and x < 5 and y >= 3 and y < 5
                            and z >= 3 and z < 5 )
                    xyz.append((x, y, z))
                    ix += 1
                iy += 1

        self.assertEqual(t_mask, g.dimensions[0]["mask"].tolist())
        self.assertEqual(xyz_mask, g.dimensions[1]["mask"].tolist())

    def test_separate_indexes(self):
        x1 = LineGenerator("x1", "mm", -1.0, 1.0, 5, False)
        y1 = LineGenerator("y1", "mm", -1.0, 1.0, 5, False)
        z1 = LineGenerator("z1", "mm", -1.0, 1.0, 5, False)
        x2 = LineGenerator("x2", "mm", -1.0, 1.0, 5, False)
        y2 = LineGenerator("y2", "mm", -1.0, 1.0, 5, False)
        x3 = LineGenerator("x3", "mm", 0, 1.0, 5, False)
        y3 = LineGenerator("y3", "mm", 0, 1.0, 5, False)
        r = CircularROI([0, 0], 1)
        e1 = Excluder(r, ["x1", "y1"])
        e2 = Excluder(r, ["y1", "z1"])
        e3 = Excluder(r, ["x1", "y1"])
        e4 = Excluder(r, ["x2", "y2"])
        e5 = Excluder(r, ["x3", "y3"])
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
        self.assertEqual(expected_mask, g.dimensions[2]["mask"].tolist())
        p = [(x/2., y/2.) for y in range_(-2, 3) for x in range_(-2, 3)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[1]["mask"].tolist())
        p = [(x/4., y/4.) for y in range_(0, 5) for x in range_(0, 5)]
        expected_mask = [x*x + y*y <= 1 for (x, y) in p]
        self.assertEqual(expected_mask, g.dimensions[0]["mask"].tolist())

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
        self.g = CompoundGenerator([self.l2, self.l1], [self.e1], [self.m1])

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

        units_dict = dict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        gen = CompoundGenerator.from_dict(_dict)

        self.assertEqual(gen.generators[0], self.l2)
        self.assertEqual(gen.generators[1], self.l1)
        self.assertEqual(gen.mutators[0], self.m1)
        self.assertEqual(gen.excluders[0], self.e1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
