import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import ROI

from pkg_resources import require
require("mock")
from mock import Mock

class ROITest(unittest.TestCase):

    def test_to_dict(self):
        roi = ROI()
        expected = {
            "typeid":"scanpointgenerator:roi/ROI:1.0"}
        self.assertEqual(expected, roi.to_dict())

    def test_register_subclass(self):
        subcls = Mock()
        ROI.register_subclass("test_id")(subcls)
        self.assertEqual(subcls, ROI._roi_lookup["test_id"])
        d = {"typeid":"test_id"}
        ROI.from_dict(d)
        subcls.from_dict.assert_called_once_with(d)

if __name__ == "__main__":
    unittest.main()
