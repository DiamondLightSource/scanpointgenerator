import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LissajousGenerator


class LissajousGeneratorTest(ScanPointGeneratorTest):

    def setUp(self):
        self.bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        self.g = LissajousGenerator(["x", "y"], "mm", self.bounding_box, 1)

    def test_init(self):
        self.assertEqual(self.g.units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [250])
        self.assertEqual(self.g.index_names, ["x_y_Lissajous"])
        self.assertEqual(self.g.axes, ["x", "y"])

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            LissajousGenerator(["x", "x"], "mm", dict(), 1)

    def test_array_positions(self):
        g = LissajousGenerator(['x', 'y'], "mm", self.bounding_box, 1, num_points=10)
        positions = [{'y': 0.0, 'x': 0.5},
                     {'y': 0.47552825814757677, 'x': 0.4045084971874737},
                     {'y': 0.2938926261462366, 'x': 0.15450849718747375},
                     {'y': -0.2938926261462365, 'x': -0.15450849718747364},
                     {'y': -0.4755282581475768, 'x': -0.40450849718747367},
                     {'y': -1.2246467991473532e-16, 'x': -0.5},
                     {'y': 0.47552825814757677, 'x': -0.4045084971874738},
                     {'y': 0.2938926261462367, 'x': -0.1545084971874738},
                     {'y': -0.2938926261462364, 'x': 0.1545084971874736},
                     {'y': -0.4755282581475769, 'x': 0.4045084971874736}]
        bounds = [{'y': -0.29389262614623657, 'x': 0.47552825814757677},
                 {'y': 0.29389262614623657, 'x': 0.4755282581475768},
                 {'y': 0.4755282581475768, 'x': 0.2938926261462366},
                 {'y': 6.123233995736766e-17, 'x': 6.123233995736766e-17},
                 {'y': -0.47552825814757677, 'x': -0.2938926261462365},
                 {'y': -0.2938926261462367, 'x': -0.47552825814757677},
                 {'y': 0.29389262614623607, 'x': -0.47552825814757682},
                 {'y': 0.4755282581475768, 'x': -0.2938926261462367},
                 {'y': 1.8369701987210297e-16, 'x': -1.2246467991473532e-16},
                 {'y': -0.4755282581475767, 'x': 0.29389262614623646},
                 {'y': -0.29389262614623674, 'x': 0.47552825814757677}]

        g.prepare_positions()
        g.prepare_bounds()
        p = [{'x':x, 'y':y} for (x, y) in zip(g.positions['x'], g.positions['y'])]
        b = [{'x':x, 'y':y} for (x, y) in zip(g.bounds['x'], g.bounds['y'])]
        self.assertEqual(positions, p)
        self.assertEqual(bounds, b)

    def test_array_positions_with_offset(self):
        g = LissajousGenerator(
            ['x', 'y'], 'mm',
            {"centre":[1., 0.], "height":1., "width":2.},
            1, num_points = 5)
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
        expected_dict = dict()
        box = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/LissajousGenerator:1.0"
        box['centre'] = [0.0, 0.0]
        box['width'] = 1.0
        box['height'] = 1.0

        expected_dict['axes'] = ["x", "y"]
        expected_dict['units'] = "mm"
        expected_dict['box'] = box
        expected_dict['num_lobes'] = 1
        expected_dict['num_points'] = 250

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        box = dict()
        box['centre'] = [0.0, 0.0]
        box['width'] = 1.0
        box['height'] = 2.0

        _dict = dict()
        _dict['axes'] = ["x", "y"]
        _dict['units'] = "mm"
        _dict['box'] = box
        _dict['num_lobes'] = 5
        _dict['num_points'] = 250

        units_dict = dict()
        units_dict['x'] = "mm"
        units_dict['y'] = "mm"

        gen = LissajousGenerator.from_dict(_dict)

        self.assertEqual(["x", "y"], gen.axes)
        self.assertEqual(["x_y_Lissajous"], gen.index_names)
        self.assertEqual(units_dict, gen.units)
        self.assertEqual(5, gen.x_freq)
        self.assertEqual(0.5, gen.x_max)
        self.assertEqual(1.0, gen.y_max)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(250, gen.size)

if __name__ == "__main__":
    unittest.main()
