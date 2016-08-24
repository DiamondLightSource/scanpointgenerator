import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.roi import ROI


class InitTest(unittest.TestCase):

    def test_variables_set(self):
        x_centre = y_centre = 0.0

        roi = ROI([x_centre, y_centre])

        self.assertEqual(x_centre, roi.centre[0])
        self.assertEqual(y_centre, roi.centre[1])

if __name__ == "__main__":
    unittest.main()
