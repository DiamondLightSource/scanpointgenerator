import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import SpiralGenerator


class SpiralGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = SpiralGenerator(['x', 'y'], ["cm", "mm"], [0.0, 0.0], 1.4, alternate=True)

    def test_init(self):
        self.assertEqual(self.g.units, dict(x="cm", y="mm"))
        self.assertEqual(self.g.axes, ["x", "y"])

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            SpiralGenerator(["x", "x"], ["mm", "mm"], [0.0, 0.0], 1.0)

    def test_array_positions(self):
        expected_x = [0.23663214944574582, -0.6440318266552169,
            -0.5596688286164636, 0.36066957248394327, 1.130650533568409,
            1.18586065489788, 0.5428735608675326]
        expected_y = [-0.3211855677650875, -0.25037538922751695,
            0.6946549630820702, 0.9919687803189761, 0.3924587351155914,
            -0.5868891557832875, -1.332029488076613,]
        expected_bx = [0.0, -0.2214272368007088, -0.7620433832656455,
            -0.13948222773063082, 0.8146440851904461, 1.2582363345925418,
            0.9334439933089926, 0.06839234794968006]
        expected_by = [0.0, -0.5189218293602549, 0.23645222432582483,
            0.9671992383675001, 0.7807653675717078, -0.09160107657707395,
            -1.0190886264001306, -1.4911377166541206]
        self.g.prepare_positions()
        self.g.prepare_bounds()
        self.assertListAlmostEqual(expected_x, self.g.positions['x'].tolist())
        self.assertListAlmostEqual(expected_y, self.g.positions['y'].tolist())
        self.assertListAlmostEqual(expected_bx, self.g.bounds['x'].tolist())
        self.assertListAlmostEqual(expected_by, self.g.bounds['y'].tolist())

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/SpiralGenerator:1.0"
        expected_dict['axes'] = ['x', 'y']
        expected_dict['units'] = ['cm', 'mm']
        expected_dict['centre'] = [0.0, 0.0]
        expected_dict['radius'] = 1.4
        expected_dict['scale'] = 1
        expected_dict['alternate'] = True

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()
        _dict['type'] = "SpiralGenerator"
        _dict['axes'] = ["x", "y"]
        _dict['units'] = ["mm", "cm"]
        _dict['centre'] = [0.0, 0.0]
        _dict['radius'] = 1.4
        _dict['scale'] = 1
        _dict['alternate'] = True

        units_dict = dict()
        units_dict['x'] = "mm"
        units_dict['y'] = "cm"

        gen = SpiralGenerator.from_dict(_dict)

        self.assertEqual(["x", "y"], gen.axes)
        self.assertEqual(units_dict, gen.units)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(1.4, gen.radius)
        self.assertEqual(1, gen.scale)

if __name__ == "__main__":
    unittest.main(verbosity=2)
