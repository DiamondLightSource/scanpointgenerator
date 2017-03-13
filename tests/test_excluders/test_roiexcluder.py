import unittest

from pkg_resources import require
require("mock")
from mock import MagicMock, patch, call

from scanpointgenerator import ROIExcluder
from scanpointgenerator.compat import np

roi_patch_path = "scanpointgenerator.core.ROI"


class TestCreateMask(unittest.TestCase):

    def setUp(self):
        self.r1 = MagicMock()
        self.r2 = MagicMock()
        self.e = ROIExcluder([self.r1, self.r2], ["x", "y"])

    def test_create_mask_returns_union_of_rois(self):
        x_points = np.array([1, 2, 3, 4])
        y_points = np.array([10, 10, 20, 20])
        self.r1.mask_points.return_value = \
            np.array([True, False, False, True])
        self.r2.mask_points.return_value = \
            np.array([False, False, True, True])
        expected_mask = np.array([True, False, True, True])

        mask = self.e.create_mask(x_points, y_points)

        r1_call_list = self.r1.mask_points.call_args_list[0][0][0]
        r2_call_list = self.r2.mask_points.call_args_list[0][0][0]
        self.assertEqual(x_points.tolist(), r1_call_list[0].tolist())
        self.assertEqual(y_points.tolist(), r1_call_list[1].tolist())
        self.assertEqual(x_points.tolist(), r2_call_list[0].tolist())
        self.assertEqual(y_points.tolist(), r2_call_list[1].tolist())
        self.assertEqual(expected_mask.tolist(), mask.tolist())


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.r1 = MagicMock()
        self.r1_dict = MagicMock()
        self.r2 = MagicMock()
        self.r2_dict = MagicMock()
        self.r1.to_dict.return_value = self.r1_dict
        self.r2.to_dict.return_value = self.r2_dict

        self.e = ROIExcluder([self.r1, self.r2], ["x", "y"])

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:excluder/ROIExcluder:1.0"
        expected_dict['rois'] = [self.r1_dict, self.r2_dict]
        expected_dict['axes'] = ["x", "y"]

        d = self.e.to_dict()

        self.assertEqual(expected_dict, d)

    @patch(roi_patch_path + '.from_dict')
    def test_from_dict(self, from_dict_mock):
        from_dict_mock.side_effect = [self.r1, self.r2]
        _dict = dict()
        _dict['rois'] = [self.r1_dict, self.r2_dict]
        _dict['axes'] = ["x", "y"]

        e = ROIExcluder.from_dict(_dict)

        from_dict_mock.assert_has_calls([call(self.r1_dict),
                                         call(self.r2_dict)])
        self.assertEqual(e.rois, [self.r1, self.r2])
        self.assertEqual(e.axes, ["x", "y"])
