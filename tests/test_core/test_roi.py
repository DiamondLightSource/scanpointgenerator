import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from scanpointgenerator import ROI

from pkg_resources import require
require("mock")
from mock import Mock

class ROITest(unittest.TestCase):

    def test_to_dict(self):
        roi = ROI()
        expected = {}
        self.assertEqual(expected, roi.to_dict())


if __name__ == "__main__":
    unittest.main()
