from collections import OrderedDict
import unittest

from scanpointgenerator.scanregion import ScanRegion

from pkg_resources import require
require("mock")
from mock import MagicMock


class ScanRegionTest(unittest.TestCase):

    def setUp(self):
        self.roi = MagicMock()
        self.scannables = ['x', 'y']
        self.sr = ScanRegion(self.roi, self.scannables)

    def test_init(self):
        self.assertEqual(self.sr.roi, self.roi)
        self.assertEqual(self.sr.scannables, self.scannables)

    def test_contains_point(self):
        d = OrderedDict()
        d['x'] = 1.0
        d['y'] = 2.0

        self.sr.contains_point(d)

        self.roi.contains_point.assert_called_once_with((1.0, 2.0))


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.r1 = MagicMock()
        self.r1_dict = MagicMock()

        self.g = ScanRegion(self.r1, ['x', 'y'])

    def test_to_dict(self):
        self.r1.to_dict.return_value = self.r1_dict

        expected_dict = OrderedDict()
        expected_dict['roi'] = self.r1_dict
        expected_dict['scannables'] = ['x', 'y']

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        self.r1_dict.from_dict.return_value = self.r1

        _dict = OrderedDict()
        _dict['roi'] = self.r1_dict
        _dict['scannables'] = ['x', 'y']

        gen = ScanRegion.from_dict(_dict)

        self.assertEqual(gen.roi, self.r1)
        self.assertEqual(gen.scannables, ['x', 'y'])
