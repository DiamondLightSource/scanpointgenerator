import unittest

from scanpointgenerator.rectangular_roi import RectangularROI


class InitTest(unittest.TestCase):

    def test_given_zero_height_then_error(self):
        expected_error_message = "Rectangle must have some size"

        with self.assertRaises(ValueError) as error:
            RectangularROI([0.0, 0.0], 0.0, 5.0)

        self.assertEqual(expected_error_message, error.exception.message)

    def test_given_zero_width_then_error(self):
        expected_error_message = "Rectangle must have some size"

        with self.assertRaises(ValueError) as error:
            RectangularROI([0.0, 0.0], 5.0, 0.0)

        self.assertEqual(expected_error_message, error.exception.message)

    def test_given_valid_params_then_set(self):

        x_centre = 1.0
        y_centre = 4.0
        height = 5.0
        width = 10.0

        rectangle = RectangularROI([x_centre, y_centre], width, height)

        self.assertEqual(rectangle.name, "Rectangle")
        self.assertEqual(rectangle.width, width)
        self.assertEqual(rectangle.height, height)
        self.assertEqual(rectangle.centre[0], x_centre)
        self.assertEqual(rectangle.centre[1], y_centre)


class ContainsPointTest(unittest.TestCase):

    def setUp(self):
        self.Rectangle = RectangularROI([0.0, 0.0], 4.0, 5.0)

        self.point = [1.0, 2.0]

    def test_given_valid_point_then_return_True(self):
        self.assertTrue(self.Rectangle.contains_point(self.point))

    def test_given_point_high_then_return_False(self):
        self.point = [5.0, 2.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_low_then_return_False(self):
        self.point = [-3.0, 2.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_left_then_return_False(self):
        self.point = [1.0, 4.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))

    def test_given_point_right_then_return_False(self):
        self.point = [1.0, -6.0]

        self.assertFalse(self.Rectangle.contains_point(self.point))
