import unittest

from scanpointgenerator.roi import ROI


class InitTest(unittest.TestCase):

    def test_variables_set(self):
        name = "Region"
        x_centre = y_centre = 0.0

        roi = ROI(name, [x_centre, y_centre])

        self.assertEqual(name, roi.name)
        self.assertEqual(x_centre, roi.centre[0])
        self.assertEqual(y_centre, roi.centre[1])
