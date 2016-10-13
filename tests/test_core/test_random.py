import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pkg_resources import require
require("mock")
from mock import patch

from test_util import ScanPointGeneratorTest
from scanpointgenerator import Random


class RandomTest(unittest.TestCase):

    @patch('scanpointgenerator.random.Random.twist')
    def test_init(self, twist_mock):
        self.RNG = Random(1)
        self.assertEqual(0, self.RNG.index)
        self.assertEqual(624, len(self.RNG.seeds))
        twist_mock.assert_called_once_with()

    def setUp(self):
        self.RNG = Random(1)

    @patch('scanpointgenerator.random.Random.twist')
    def test_generate_number(self, twist_mock):
        self.RNG.seeds[0] = 1234567890
        response = self.RNG.generate_number()

        self.assertEqual(1284973367, response)

        for i in range(624):
            self.RNG.generate_number()

        twist_mock.assert_called_once_with()

    def test_twist(self):
        self.RNG.seeds = [1, 54235326, 723456923, 23489293] + [0]*620
        expected_seeds = [27117663, 2357672210, 2579203417, 0] + [0]*620

        self.RNG.twist()

        for i in range(5):
            self.assertEqual(expected_seeds[i], self.RNG.seeds[i])

    def test_random(self):
        self.RNG.seeds[0] = 1234567890

        response = self.RNG.random()
        self.assertAlmostEqual(0.633794821, response, places=10)
        response = self.RNG.random()
        self.assertAlmostEqual(0.316782824, response, places=10)
        response = self.RNG.random()
        self.assertAlmostEqual(-0.789226097, response, places=10)
        response = self.RNG.random()
        self.assertAlmostEqual(-0.366964996, response, places=10)
        response = self.RNG.random()
        self.assertAlmostEqual(0.948058921, response, places=10)
        response = self.RNG.random()
        self.assertAlmostEqual(0.436480924, response, places=10)

    def test_int32(self):
        response = self.RNG._int32(0x100000001)

        self.assertEqual(1, response)

if __name__ == "__main__":
    unittest.main()
