import unittest
import os
import sys

# module import
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class ScanPointGeneratorTest(unittest.TestCase):
    def assertListAlmostEqual(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            if type(a) in (list, tuple):
                self.assertEqual(type(a), type(e))
                self.assertListAlmostEqual(a, e)
            else:
                self.assertAlmostEqual(a, e, delta=0.000001)

    def assertIteratorProduces(self, iterator, all_expected):
        for expected in all_expected:
            actual = iterator.next()
            if type(actual) in (list, tuple):
                self.assertListAlmostEqual(actual, expected)
            else:
                self.assertAlmostEqual(actual, expected, delta=0.000001)
        self.assertRaises(StopIteration, iterator.next)
