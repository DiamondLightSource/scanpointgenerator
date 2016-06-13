import unittest
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.maskedgenerator import MaskedGenerator
from scanpointgenerator import NestedGenerator, LineGenerator

from pkg_resources import require
require("mock")
from mock import MagicMock


class MaskedGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.roi = RectangularROI([0.0, 0.0], 5.0, 8.0)
        x = LineGenerator("x", "mm", 0.0, 9.0, 10)
        y = LineGenerator("y", "mm", 0.0, 9.0, 10)
        self.nest = NestedGenerator(y, x, alternate_direction=True)

    def test_init(self):
        gen = MaskedGenerator(self.nest, self.roi)
        self.assertEqual(self.nest, gen.generator)
        self.assertEqual(self.roi, gen.roi)

    def test_correct_calls_made(self):
        nest = MagicMock()
        point = MagicMock()
        nest.iterator.return_value = [point]
        roi = MagicMock()
        roi.contains_point.return_value = True

        gen = MaskedGenerator(nest, roi)
        for response in gen.iterator():
            self.assertEqual(point, response)

        nest.iterator.assert_called_once_with()
        roi.contains_point.assert_called_once_with(point)

    def test_given_points_then_filter(self):
        gen = MaskedGenerator(self.nest, self.roi)

        expected_points = [{'y': 0.0, 'x': 0.0}, {'y': 0.0, 'x': 1.0}, {'y': 0.0, 'x': 2.0},
                           {'y': 1.0, 'x': 2.0}, {'y': 1.0, 'x': 1.0}, {'y': 1.0, 'x': 0.0},
                           {'y': 2.0, 'x': 0.0}, {'y': 2.0, 'x': 1.0}, {'y': 2.0, 'x': 2.0},
                           {'y': 3.0, 'x': 2.0}, {'y': 3.0, 'x': 1.0}, {'y': 3.0, 'x': 0.0},
                           {'y': 4.0, 'x': 0.0}, {'y': 4.0, 'x': 1.0}, {'y': 4.0, 'x': 2.0}]

        for i, point in enumerate(gen.iterator()):
            self.assertEqual(expected_points[i], point.positions)
