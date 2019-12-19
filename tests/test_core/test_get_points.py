import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator import CircularROI, ROIExcluder
from scanpointgenerator import RandomOffsetMutator
from scanpointgenerator.compat import np

class GetPointsTest(ScanPointGeneratorTest):

    def setUp(self):
        l1 = LineGenerator("x", "mm", 0, 5, 5)
        l2 = LineGenerator("y", "nm", 0, 5, 5)
        l3 = LineGenerator("z", "mm", 0, 5, 5)
        self.comp = CompoundGenerator([l1, l2, l3], [], [], 5, True, 7)
        self.comp.prepare()

    def test_simple_points(self):
        points= self.comp.get_points(7, 12)
        self.assertEqual(list([[0, 1, 2],[0, 1, 3],[0, 1, 4],[0, 2, 0],[0, 2, 1]]), points.indexes.tolist())
        self.assertEqual(list([0., 0., 0., 0., 0.]), points.lower['x'].tolist())
        self.assertEqual(list([1.25, 1.25, 1.25, 2.5 , 2.5]), points.lower['y'].tolist())
        self.assertEqual(list([1.875,  3.125,  4.375, -0.625,  0.625]), points.lower['z'].tolist())
        self.assertTrue(np.all(np.full(5, 5) == points.duration))
        self.assertTrue(np.all(np.full(5, 7) == points.delay_after))
    
    def test_bulk(self):
        points= self.comp.get_points(42, 59)
        for a in range(42, 59):
            self.assertListAlmostEqual(self.comp.get_point(a).indexes, points.indexes[a-42])
            for axis in ["x", "y", "z"]:
                self.assertEqual(self.comp.get_point(a).lower[axis], points.lower[axis][a-42])
                self.assertEqual(self.comp.get_point(a).upper[axis], points.upper[axis][a-42])
                self.assertEqual(self.comp.get_point(a).positions[axis], points.positions[axis][a-42])
            
    def test_alternating(self):
        l1 = LineGenerator("x", "mm", 0, 5, 5)
        l2 = LineGenerator("y", "nm", 0, 5, 5, True)
        l3 = LineGenerator("z", "mm", 0, 5, 5)
        comp = CompoundGenerator([l1, l2, l3], [], [], 5)
        comp.prepare()
        self.assertEqual(list([[0,0,0],[0,0,1],[0,0,2],[0,0,3],[0,0,4],[0,1,0],[0,1,1],[0,1,2],[0,1,3],[0,1,4],
                               [0,2,0]]), comp.get_points(0, 11).indexes.tolist())
        self.assertEqual(list([[0,3,1],[0,3,2],[0,3,3],[0,3,4],[0,4,0],[0,4,1],[0,4,2],[0,4,3],[0,4,4],[1,4,0],
                               [1,4,1]]), comp.get_points(16, 27).indexes.tolist())

    def test_alternating_bounds(self):
        l1 = LineGenerator("x", "mm", 0, 0.5, 3, True)
        l2 = LineGenerator("y", "nm", 0, 0.1, 2)
        comp = CompoundGenerator([l2, l1], [], [])
        comp.prepare()
        points = comp.get_points(0, 6)
        self.assertEqual(list([0., 0., 0., 0.1, 0.1, 0.1]), points.lower["y"].tolist())
        self.assertEqual(list([0., 0., 0., 0.1, 0.1, 0.1]), points.upper["y"].tolist())
        self.assertEqual(list([-0.125, 0.125, 0.375, 0.625, 0.375, 0.125]), points.lower["x"].tolist())
        self.assertEqual(list([0.125, 0.375, 0.625, 0.375, 0.125, -0.125]), points.upper["x"].tolist())

    def test_backwards(self):
        l1 = LineGenerator("x", "mm", 0, 0.5, 3, True)
        l2 = LineGenerator("y", "nm", 0, 0.1, 2)
        comp = CompoundGenerator([l2, l1], [], [])
        comp.prepare()
        fpoints = comp.get_points(0, 6)
        bpoints = comp.get_points(5,-1)
        for i in range(0,5):
            for axis in fpoints.positions:
                self.assertEqual(fpoints.positions[axis][i], bpoints.positions[axis][5-i])
                self.assertEqual(fpoints.lower[axis][i], bpoints.lower[axis][5-i])
                self.assertEqual(fpoints.upper[axis][i], bpoints.upper[axis][5-i])
            self.assertTrue(np.all(fpoints.indexes[i] == bpoints.indexes[5-i]))

    def test_roi(self):
        l1 = LineGenerator("x", "mm", 0.5, 5.5, 6)
        l2 = LineGenerator("y", "mm", 0.5, 5.5, 6)
        r1 = CircularROI([2.5, 2.5], 1.01)
        e = ROIExcluder([r1], ["x", "y"])
        self.comp = CompoundGenerator([l1, l2], [e], [], 5, True, 7)
        self.comp.prepare()
        # Comp.size = 5, only these points included
        y = [2.5, 1.5, 2.5, 3.5, 2.5]
        y_up = [3, 2, 3, 4, 3]
        y_dn = [2, 1, 2, 3, 2]
        x = [1.5, 2.5, 2.5, 2.5, 3.5]
        points= self.comp.get_points(0,5)
        self.assertTrue(np.all([0,1,2,3,4] == points.indexes))
        self.assertTrue(np.all(x == points.positions["x"]))
        self.assertTrue(np.all(x == points.lower["x"]))
        self.assertTrue(np.all(x == points.upper["x"]))
        self.assertTrue(np.all(y == points.positions["y"]))
        self.assertTrue(np.all(y_dn == points.lower["y"]))
        self.assertTrue(np.all(y_up == points.upper["y"]))
        
    def test_random_offset(self):
        l1 = LineGenerator("x", "mm", 0.5, 5.5, 6)
        l2 = LineGenerator("y", "mm", 0.5, 5.5, 6)
        m1 = RandomOffsetMutator(12, ["x", "y"], [0.1, 0.1])
        self.comp = CompoundGenerator([l1, l2], [], [m1], 5, True, 7)
        self.comp.prepare()
        for i in range(8):
            self.assertAlmostEqual([0.458672, 1.543717, 2.582332, 3.514304, 4.558364, 5.528023, 0.574501, 1.452161][i],
                               self.comp.get_points(0, 8).positions["y"][i], delta=0.0001)

    def test_slicing(self):
        l1 = LineGenerator("x", "mm", 0.5, 5.5, 6)
        l2 = LineGenerator("y", "mm", 0.5, 5.5, 6)
        m1 = RandomOffsetMutator(12, ["x", "y"], [0.1, 0.1])
        self.comp = CompoundGenerator([l1, l2], [], [m1], 5, True, 7)
        self.comp.prepare()
        # Comp.size = 5, only these points included
        points= self.comp.get_points(0, 8)
        self.assertEqual(8, len(points))
        self.assertAlmostEqual([0.458672], points[0].positions["y"], delta=0.0001)
        for i in [0, 1]:
            self.assertAlmostEqual([0.458672, 1.543717][i], points[0:2].positions["y"][i], delta=0.0001)
            self.assertAlmostEqual([0.58572882, 0.54016338][i], points[4:2:-1].positions["x"][i], delta=0.0001)
        self.assertAlmostEqual(1.46179521, points[-1].positions["x"])
        for i in range(4):
            self.assertAlmostEqual([1.461795, 0.565178, 0.540163, 0.430533][i]
                                   , points[-1:0:-2].positions["x"][i], delta=0.0001)