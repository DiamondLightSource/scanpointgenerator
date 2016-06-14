import unittest
from scanpointgenerator.point import Point
from scanpointgenerator.circular_roi import CircularROI


class InitTest(unittest.TestCase):

    def test_given_zero_radius_then_error(self):
        expected_error_message = "Circle must have some size"

        with self.assertRaises(ValueError) as error:
            CircularROI([0.0, 0.0], 0.0)

        self.assertEqual(expected_error_message, error.exception.message)

    def test_given_valid_params_then_set(self):

        x_centre = 1.0
        y_centre = 4.0
        radius = 5.0

        circle = CircularROI([x_centre, y_centre], radius)

        self.assertEqual(circle.name, "Circle")
        self.assertEqual(circle.radius, radius)
        self.assertEqual(circle.centre[0], x_centre)
        self.assertEqual(circle.centre[1], y_centre)


class ContainsPointTest(unittest.TestCase):

    def setUp(self):
        self.Circle = CircularROI([5.0, 15.0], 5.0)

        self.point = Point()
        self.point.positions['x'] = 7.0
        self.point.positions['y'] = 11.0

    def test_given_valid_point_then_return_True(self):
        self.assertTrue(self.Circle.contains_point(self.point))

    def test_given_point_outside_then_return_False(self):
        self.point.positions['x'] = 9.0

        self.assertFalse(self.Circle.contains_point(self.point))
