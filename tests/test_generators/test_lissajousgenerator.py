import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LissajousGenerator


class LissajousGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        g = LissajousGenerator(["x", "y"], ["mm", "cm"], [0., 0.], [1., 1.], 1)
        self.assertEqual(g.units, dict(x="mm", y="cm"))
        self.assertEqual(g.axes, ["x", "y"])

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            LissajousGenerator(["x", "x"], ["mm", "mm"], [0., 0,], [1., 1.], 1)

    def test_array_positions(self):
        g = LissajousGenerator(['x', 'y'], ["mm", "mm"], [0., 0.], [1., 1.], 1, size=10)
        expected_x = [0.5, 0.4045084971874737, 0.15450849718747375,
            -0.15450849718747364, -0.40450849718747367, -0.5,
            -0.4045084971874738, -0.1545084971874738, 0.1545084971874736,
            0.4045084971874736]
        expected_y = [0.0, 0.47552825814757677, 0.2938926261462366,
            -0.2938926261462365, -0.4755282581475768, -1.2246467991473532e-16,
            0.47552825814757677, 0.2938926261462367, -0.2938926261462364,
           -0.4755282581475769]
        expected_bx = [0.47552825814757677, 0.4755282581475768,
            0.2938926261462366, 6.123233995736766e-17, -0.2938926261462365,
            -0.47552825814757677, -0.47552825814757682, -0.2938926261462367,
            -1.2246467991473532e-16, 0.29389262614623646, 0.47552825814757677]
        expected_by = [-0.29389262614623657, 0.29389262614623657,
            0.4755282581475768, 6.123233995736766e-17, -0.47552825814757677,
            -0.2938926261462367, 0.29389262614623607, 0.4755282581475768,
            1.8369701987210297e-16, -0.4755282581475767, -0.29389262614623674]

        g.prepare_positions()
        g.prepare_bounds()
        self.assertListAlmostEqual(expected_x, g.positions['x'].tolist())
        self.assertListAlmostEqual(expected_y, g.positions['y'].tolist())
        self.assertListAlmostEqual(expected_bx, g.bounds['x'].tolist())
        self.assertListAlmostEqual(expected_by, g.bounds['y'].tolist())

    def test_array_positions_with_offset(self):
        g = LissajousGenerator(
            ['x', 'y'], ['mm', 'mm'], [1., 0.,], [2., 1.], 1, size=5)
        g.prepare_positions()
        g.prepare_bounds()
        expected_x = [2.0, 1.3090169943749475, 0.19098300532505266,
            0.19098300532505266, 1.3090169943749475]
        expected_y = [0.0, 0.2938926261462366, -0.4755282581475768,
            0.47552825814757677, -0.2938926261462364]
        expected_bx = [1.8090169943749475, 1.8090169943749475,
            0.6909830056250528, 0.0,
            0.6909830056250523, 1.8090169943749472]
        expected_by = [-0.47552825814757677, 0.47552825814757677,
            -0.2938926261462365, -1.2246467991473532e-16,
            0.2938926261462367, -0.4755282581475769]
        self.assertListAlmostEqual(expected_x, g.positions['x'].tolist())
        self.assertListAlmostEqual(expected_y, g.positions['y'].tolist())
        self.assertListAlmostEqual(expected_bx, g.bounds['x'].tolist())
        self.assertListAlmostEqual(expected_by, g.bounds['y'].tolist())

    def test_to_dict(self):
        bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        g = LissajousGenerator(["x", "y"], ["mm", "cm"], [0., 0.], [1., 1.], 1)
        expected_dict = dict()
        box = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/LissajousGenerator:1.0"

        expected_dict['axes'] = ["x", "y"]
        expected_dict['units'] = ["mm", "cm"]
        expected_dict['centre'] = [0., 0.]
        expected_dict['span'] = [1., 1.]
        expected_dict['lobes'] = 1
        expected_dict['size'] = 250

        d = g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()
        _dict['axes'] = ["x", "y"]
        _dict['units'] = ["cm", "mm"]
        _dict['centre'] = [0.0, 0.0]
        _dict['span'] = [1., 2.]
        _dict['lobes'] = 5
        _dict['size'] = 250

        units_dict = dict()
        units_dict['x'] = "cm"
        units_dict['y'] = "mm"

        gen = LissajousGenerator.from_dict(_dict)

        self.assertEqual(["x", "y"], gen.axes)
        self.assertEqual(units_dict, gen.units)
        self.assertEqual(5, gen.x_freq)
        self.assertEqual(0.5, gen.x_max)
        self.assertEqual(1.0, gen.y_max)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(250, gen.size)

if __name__ == "__main__":
    unittest.main(verbosity=2)
