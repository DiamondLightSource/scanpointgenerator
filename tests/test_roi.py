import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.roi import ROI

from pkg_resources import require
require("mock")
from mock import Mock

class ROITest(unittest.TestCase):

    def test_variables_set(self):
        x_centre = y_centre = 0.0

        roi = ROI([x_centre, y_centre])

        self.assertEqual(x_centre, roi.centre[0])
        self.assertEqual(y_centre, roi.centre[1])

    def test_to_dict(self):
        roi = ROI([1.1, 2.2])
        expected = {
            "typeid":"scanpointgenerator:roi/ROI:1.0",
            "centre":[1.1, 2.2]}
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
