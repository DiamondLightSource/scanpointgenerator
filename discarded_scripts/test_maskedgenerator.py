from collections import OrderedDict
import unittest

from scanpointgenerator import MaskedGenerator, CompoundGenerator, LineGenerator
from scanpointgenerator.rectangular_roi import RectangularROI

from pkg_resources import require
require("mock")
from mock import MagicMock, patch


class MaskedGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.roi = RectangularROI([0.0, 0.0], 5.0, 8.0)
        x = LineGenerator("x", "mm", 0.0, 9.0, 10)
        y = LineGenerator("y", "mm", 0.0, 9.0, 10)
        self.nest = CompoundGenerator(y, x, alternate_direction=True)

    def test_init(self):
        gen = MaskedGenerator(self.nest, [self.roi])
        self.assertEqual(self.nest, gen.generator)
        self.assertEqual(self.roi, gen.rois[0])

    def test_correct_calls_made(self):
        nest = MagicMock()
        point = MagicMock()
        nest.iterator.return_value = [point]
        roi = MagicMock()
        roi.contains_point.return_value = True

        gen = MaskedGenerator(nest, [roi])
        for response in gen.iterator():
            self.assertEqual(point, response)

        nest.iterator.assert_called_once_with()
        roi.contains_point.assert_called_once_with(point)

    def test_given_points_then_filter(self):
        gen = MaskedGenerator(self.nest, [self.roi])

        expected_points = [{'y': 0.0, 'x': 0.0}, {'y': 0.0, 'x': 1.0}, {'y': 0.0, 'x': 2.0},
                           {'y': 1.0, 'x': 2.0}, {'y': 1.0, 'x': 1.0}, {'y': 1.0, 'x': 0.0},
                           {'y': 2.0, 'x': 0.0}, {'y': 2.0, 'x': 1.0}, {'y': 2.0, 'x': 2.0},
                           {'y': 3.0, 'x': 2.0}, {'y': 3.0, 'x': 1.0}, {'y': 3.0, 'x': 0.0},
                           {'y': 4.0, 'x': 0.0}, {'y': 4.0, 'x': 1.0}, {'y': 4.0, 'x': 2.0}]

        for i, point in enumerate(gen.iterator()):
            self.assertEqual(expected_points[i], point.positions)


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.roi = MagicMock()
        self.roi_dict = MagicMock()
        self.line = MagicMock()
        self.line_dict = MagicMock()
        self.gen = MaskedGenerator(self.line, [self.roi])

    def test_to_dict(self):
        self.roi.to_dict.return_value = self.roi_dict
        self.line.to_dict.return_value = self.line_dict

        expected_dict = OrderedDict()
        expected_dict['type'] = "MaskedGenerator"
        expected_dict['generator'] = self.line_dict
        expected_dict['rois'] = [self.roi_dict]

        d = self.gen.to_dict()

        self.assertEqual(expected_dict, d)

    @patch('scanpointgenerator.maskedgenerator.ROI')
    @patch('scanpointgenerator.maskedgenerator.Generator')
    def test_from_dict(self, SPG_mock, ROI_mock):
        SPG_mock.from_dict.return_value = self.line
        ROI_mock.from_dict.return_value = self.roi

        _dict = OrderedDict()
        _dict['type'] = "MaskedGenerator"
        _dict['generator'] = self.line_dict
        _dict['rois'] = [self.roi_dict]

        gen = MaskedGenerator.from_dict(_dict)

        self.assertEqual(self.roi, gen.rois[0])
        self.assertEqual(self.line, gen.generator)
