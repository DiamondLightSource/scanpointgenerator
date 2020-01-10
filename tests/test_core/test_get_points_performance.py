import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
import time

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator, StaticPointGenerator, LissajousGenerator, SpiralGenerator
from scanpointgenerator import CircularROI, RectangularROI, ROIExcluder
from scanpointgenerator import RandomOffsetMutator

# Jython gets 3x as long
TIMELIMIT = 3 if os.name == "java" else 1
# Goal is 10khz, 1s per 10,000(10e4) points


class GetPointsPerformanceTest(ScanPointGeneratorTest):

    def test_90_thousand_time_constraint(self):
        z = LineGenerator("z", "mm", 0, 1, 300, True)
        w = LineGenerator("w", "mm", 0, 1, 300, True)
        g = CompoundGenerator([z, w], [], [])
        g.prepare() # 9e4 points
        start_time = time.time()
        C = g.get_points(0, 90000)
        end_time = time.time()
        self.assertLess(end_time - start_time, TIMELIMIT*9)
        
    def test_30_thousand_time_constraint_with_outer(self):
        a = StaticPointGenerator(1)
        z = LineGenerator("z", "mm", 0, 1, 300, True)
        w = LineGenerator("w", "mm", 0, 1, 300, True)
        g = CompoundGenerator([a, z, w], [], [])
        g.prepare() # 9e4 points
        start_time = time.time()
        C = g.get_points(0, 30000)
        end_time = time.time()
        self.assertLess(end_time - start_time, TIMELIMIT*3)
        
    def test_30_thousand_time_constraint_with_inner(self):
        a = StaticPointGenerator(1)
        z = LineGenerator("z", "mm", 0, 1, 300, True)
        w = LineGenerator("w", "mm", 0, 1, 300, True)
        g = CompoundGenerator([z, w, a], [], [])
        g.prepare() # 9e4 points 
        start_time = time.time()
        C = g.get_points(0, 30000)
        end_time = time.time()
        self.assertLess(end_time - start_time, TIMELIMIT*3)
    
    @unittest.skip("Unsuitable")
    def test_1_million_time_constraint_complex(self):
        a = LineGenerator("a", "mm", 0, 1, 10, True)
        b = LineGenerator("b", "mm", 0, 1, 10)
        c = LineGenerator("c", "mm", 0, 1, 10) 
        d = LineGenerator("d", "mm", 0, 1, 10)
        e = LineGenerator("e", "mm", 0, 1, 10) 
        f = LineGenerator("f", "mm", 0, 1, 10)
        g = CompoundGenerator([b, c, d, e, f, a], [], [])
        g.prepare() # 1e6 points
        start_time = time.time()
        C = g.get_points(0, 1000000)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*100)

    @unittest.skip("Unsuitable")
    def test_small_time_constraint_complex(self):
        a = LineGenerator("a", "mm", 0, 1, 10, True)
        b = LineGenerator("b", "mm", 0, 1, 10)
        c = LineGenerator("c", "mm", 0, 1, 10) 
        d = LineGenerator("d", "mm", 0, 1, 10)
        e = LineGenerator("e", "mm", 0, 1, 10) 
        f = LineGenerator("f", "mm", 0, 1, 10)
        g = CompoundGenerator([b, c, d, e, f, a], [], [])
        g.prepare() # 1e6 points
        start_time = time.time()
        C = g.get_points(0, 1)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*1e-4)
        start_time = time.time()
        C = g.get_points(0, 10)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*1e-3)
        start_time = time.time()
        C = g.get_points(0, 100)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*1e-2)
        
    def test_roi_time_constraint(self):
        a = LineGenerator("a", "mm", 0, 1, 300, True)
        b = LineGenerator("b", "mm", 0, 1, 300)
        r1 = CircularROI([0.25, 0.33], 0.1)
        e1 = ROIExcluder([r1], ["a", "b"])
        g = CompoundGenerator([b, a], [e1], [])
        g.prepare() # ~2,800 points
        start_time = time.time()
        C = g.get_points(0, 1000)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*0.1)
        start_time = time.time()
        C = g.get_points(0, 2800)
        end_time = time.time()
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, TIMELIMIT*0.28)
    
    @unittest.skip("Unsuitable")
    def test_time_constraint_complex(self):
        a = LineGenerator("a", "eV", 0, 1, 10)
        b = LineGenerator("b", "rad", 0, 1, 10)
        c = LissajousGenerator(["c", "d"], ["mm", "cm"], [0, 0], [5, 5], 3, 10) 
        d = SpiralGenerator(["e", "f"], ["mm", "s"], [10, 5], 7, 0.6)
        e = LineGenerator("g", "mm", 0, 1, 10) 
        f = LineGenerator("h", "mm", 0, 5, 20)
        r1 = CircularROI([0.2, 0.2], 0.1)
        r2 = CircularROI([0.4, 0.2], 0.1)
        r3 = CircularROI([0.6, 0.2], 0.1)
        e1 = ROIExcluder([r1, r2, r3], ["a", "b"])
        m1 = RandomOffsetMutator(12, ["a"], [0.1])
        m2 = RandomOffsetMutator(200, ["c", "f"], [0.01, 0.5])

        g = CompoundGenerator([c, d, e, f, b, a], [e1], [m1, m2])
        g.prepare() # 1e6 points
        for i in [1, 2, 3, 4, 5, 6]:
            p = 10**i
            start_time = time.time()
            g.get_points(0, p)
            end_time = time.time()
            self.assertLess(end_time - start_time, TIMELIMIT*p/1e4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
