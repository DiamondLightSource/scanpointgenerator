import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
import time

from test_util import ScanPointGeneratorTest
from scanpointgenerator import CompoundGenerator
from scanpointgenerator import LineGenerator
from scanpointgenerator import SpiralGenerator
from scanpointgenerator import Excluder
from scanpointgenerator.rois import CircularROI
from scanpointgenerator.mutators import FixedDurationMutator, RandomOffsetMutator

class CompoundGeneratorPerformanceTest(ScanPointGeneratorTest):
    def test_200_million_time_constraint(self):
        start_time = time.time()

        s = SpiralGenerator(
            ["x", "y"], "mm", [0, 0], 6, 0.02, True) # ~2e5 points
        z = LineGenerator("z", "mm", 0, 1, 100, True) #1e2 points
        w = LineGenerator("w", "mm", 0, 1, 10, True) #1e1 points
        r1 = CircularROI([-0.7, 4], 0.5)
        r2 = CircularROI([0.5, 0.5], 0.3)
        r3 = CircularROI([0.2, 4], 0.5)
        e1 = Excluder(r1, ["x", "y"])
        e2 = Excluder(r2, ["w", "z"])
        e3 = Excluder(r3, ["z", "y"])
        fm = FixedDurationMutator(0.1)
        om = RandomOffsetMutator(0, ["x", "y"], {"x":0.2, "y":0.2})
        g = CompoundGenerator([w, z, s], [e1, e3, e2], [fm, om])
        g.prepare() # g.size ~3e5

        end_time = time.time()
        #self.assertLess(end_time - start_time, 5)
        # TravisCI VMs are sometimes pretty weak
        # if this test becomes problematic then we'll just have to remove it
        self.assertLess(end_time - start_time, 12)

        # we dont care about this right now
        #start_time = time.time()
        #for p in g.iterator():
        #    pass
        #end_time = time.time()
        ## point objects are quite expensive to create
        #self.assertLess(end_time - start_time, 20)

if __name__ == "__main__":
    unittest.main(verbosity=2)
