import unittest
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.factory import Factory
from scanpointgenerator import NestedGenerator, LineGenerator


class FactoryTest(unittest.TestCase):

    def setUp(self):
        self.roi = RectangularROI([0.0, 0.0], 5.0, 8.0)

        x = LineGenerator("x", "mm", 0.0, 1.0, 10)
        y = LineGenerator("y", "mm", 0.0, 1.0, 10)
        self.g = NestedGenerator(y, x, snake=True)

    def test_given_points_then_filter(self):

        expected_points = [{'y': 0.0, 'x': 0.0}, {'y': 0.0, 'x': 1.0}, {'y': 0.0, 'x': 2.0},
                           {'y': 1.0, 'x': 2.0}, {'y': 1.0, 'x': 1.0}, {'y': 1.0, 'x': 0.0},
                           {'y': 2.0, 'x': 0.0}, {'y': 2.0, 'x': 1.0}, {'y': 2.0, 'x': 2.0},
                           {'y': 3.0, 'x': 2.0}, {'y': 3.0, 'x': 1.0}, {'y': 3.0, 'x': 0.0},
                           {'y': 4.0, 'x': 0.0}, {'y': 4.0, 'x': 1.0}, {'y': 4.0, 'x': 2.0}]

        factory = Factory(self.g, self.roi)

        for i, point in enumerate(factory.create_points()):
            self.assertEqual(expected_points[i], point.positions)
