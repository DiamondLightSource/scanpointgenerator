import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import Excluder

from pkg_resources import require
require("mock")
from mock import MagicMock


class ExcluderTest(unittest.TestCase):

    def setUp(self):
        self.roi = MagicMock()
        self.scannables = ['x', 'y']
        self.e = Excluder(self.roi, self.scannables)

    def test_init(self):
        self.assertEqual(self.e.roi, self.roi)
        self.assertEqual(self.e.scannables, self.scannables)

    def test_contains_point(self):
        d = dict()
        d['x'] = 1.0
        d['y'] = 2.0

        self.e.contains_point(d)

        self.roi.contains_point.assert_called_once_with((1.0, 2.0))


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.r1 = MagicMock()
        self.r1_dict = MagicMock()

        self.e = Excluder(self.r1, ['x', 'y'])

    def test_to_dict(self):
        self.r1.to_dict.return_value = self.r1_dict

        expected_dict = dict()
        expected_dict['roi'] = self.r1_dict
        expected_dict['scannables'] = ['x', 'y']

        d = self.e.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        self.r1_dict.from_dict.return_value = self.r1

        _dict = dict()
        _dict['roi'] = self.r1_dict
        _dict['scannables'] = ['x', 'y']

        e = Excluder.from_dict(_dict)

        self.assertEqual(e.roi, self.r1)
        self.assertEqual(e.scannables, ['x', 'y'])

if __name__ == "__main__":
    unittest.main()
