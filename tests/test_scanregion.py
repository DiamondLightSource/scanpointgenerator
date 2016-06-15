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
