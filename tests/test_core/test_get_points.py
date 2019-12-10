import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator, Generator
from scanpointgenerator import LineGenerator, StaticPointGenerator
from scanpointgenerator import Point
from scanpointgenerator.compat import range_, np

class get_points_test(ScanPointGeneratorTest):

    def setUp(self):
        l1 = LineGenerator("x", "mm", 0, 5, 5)
        l2 = LineGenerator("y", "nm", 0, 5, 5)
        l3 = LineGenerator("z", "mm", 0, 5, 5)
        self.comp = CompoundGenerator([l1, l2, l3], [], [], 5)
        self.comp.prepare()

    def simple_points_test(self):
        C = self.comp.get_points(7, 12)
        self.assertEqual(C.indexes, [[0, 1, 2],[0, 1, 3],[0, 1, 4],[0, 2, 0],[0, 2, 1]])
        self.assertEqual(C.lower, {'y': array([1.25, 1.25, 1.25, 2.5 , 2.5 ]), 'x': array([0., 0., 0., 0., 0.]), 'z': array([ 1.875,  3.125,  4.375, -0.625,  0.625])})
        self.assertEqual(C.delay_after, np.full(5, 5))
    
    def bulk_test(self):
        C = self.comp.get_points(42, 59)
        for a in range(42, 59):
            self.assertEquals(C.indexes[a], self.comp.get_point(a).indexes)
            self.assertEquals(C.lower[a], self.comp.get_point(a).lower)
            self.assertEquals(C.upper[a],  self.comp.get_point(a).upper)
            self.assertEquals(C.positions,  self.comp.get_point(a).positions)
            
    def alternating_test(self):
        l1 = LineGenerator("x", "mm", 0, 5, 5)
        l2 = LineGenerator("y", "nm", 0, 5, 5, True)
        l3 = LineGenerator("z", "mm", 0, 5, 5)
        comp = CompoundGenerator([l1, l2, l3], [], [], 5)
        comp.prepare()
        self.assertEqual(comp.get_points(0, 11),[[0,0,0],[0,0,1],[0,0,2],[0,0,3],[0,0,4],[0,1,0],[0,1,1],[0,1,2],[0,1,3],[0,1,4]])
        self.assertEqual(comp.get_points(16, 27),[[0,3,4],[0,4,0],[0,4,1],[0,4,2],[0,4,3],[0,4,4],[1,4,0],[1,4,1],[1,4,2],[1,4,3],[1,4,4]]) 