import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.mutators import FixedDurationMutator

from pkg_resources import require
require("mock")
from mock import Mock


class FixedDurationMutatorTest(unittest.TestCase):

    def test_init(self):
        duration = Mock()
        m = FixedDurationMutator(duration)
        self.assertIs(duration, m.duration)

    def test_to_dict(self):
        duration = Mock()
        m = FixedDurationMutator(duration)
        expected = {
            "typeid":"scanpointgenerator:mutator/FixedDurationMutator:1.0",
            "duration":duration}
        self.assertEqual(expected, m.to_dict())

    def test_from_dict(self):
        duration = Mock()
        d = {
            "typeid":"scanpointgenerator:mutator/FixedDurationMutator:1.0",
            "duration":duration}
        m = FixedDurationMutator.from_dict(d)
        self.assertIs(duration, m.duration)

    def test_mutate(self):
        duration = Mock()
        m = FixedDurationMutator(duration)
        points = [Mock(), Mock(), Mock()]
        mutated_points = list(m.mutate(iter(points)))
        self.assertEqual(points, mutated_points)
        for p in mutated_points:
            self.assertIs(duration, p.duration)

if __name__ == "__main__":
    unittest.main()
