import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import LissajousGenerator


class LissajousGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        self.g = LissajousGenerator(["x", "y"], "mm", self.bounding_box, 1)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [250])
        self.assertEqual(self.g.index_names, ["x_y_Lissajous"])
        self.assertEqual(self.g.axes, ["x", "y"])

    def test_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            LissajousGenerator(["x", "x"], "mm", dict(), 1)

    def test_iterator(self):
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
        lower = [{'y': -0.29389262614623657, 'x': 0.47552825814757677},
                 {'y': 0.29389262614623657, 'x': 0.4755282581475768},
                 {'y': 0.4755282581475768, 'x': 0.2938926261462366},
                 {'y': 6.123233995736766e-17, 'x': 6.123233995736766e-17},
                 {'y': -0.47552825814757677, 'x': -0.2938926261462365},
                 {'y': -0.2938926261462367, 'x': -0.47552825814757677},
                 {'y': 0.29389262614623646, 'x': -0.4755282581475768},
                 {'y': 0.4755282581475768, 'x': -0.2938926261462367},
                 {'y': 1.8369701987210297e-16, 'x': -1.2246467991473532e-16},
                 {'y': -0.4755282581475767, 'x': 0.29389262614623646}]
        upper = [{'y': 0.29389262614623657, 'x': 0.4755282581475768},
                 {'y': 0.4755282581475768, 'x': 0.2938926261462366},
                 {'y': 6.123233995736766e-17, 'x': 6.123233995736766e-17},
                 {'y': -0.47552825814757677, 'x': -0.2938926261462365},
                 {'y': -0.2938926261462367, 'x': -0.47552825814757677},
                 {'y': 0.29389262614623646, 'x': -0.4755282581475768},
                 {'y': 0.4755282581475768, 'x': -0.2938926261462367},
                 {'y': 1.8369701987210297e-16, 'x': -1.2246467991473532e-16},
                 {'y': -0.4755282581475767, 'x': 0.29389262614623646},
                 {'y': -0.29389262614623674, 'x': 0.47552825814757677}]
        indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        for i, p in enumerate(g.iterator()):
            self.assertEqual(p.positions, positions[i])
            self.assertEqual(p.lower, lower[i])
            self.assertEqual(p.upper, upper[i])
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 9)

    def test_to_dict(self):
        expected_dict = dict()
        box = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/LissajousGenerator:1.0"
        box['centre'] = [0.0, 0.0]
        box['width'] = 1.0
        box['height'] = 1.0

        expected_dict['names'] = ["x", "y"]
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
        _dict['names'] = ["x", "y"]
        _dict['units'] = "mm"
        _dict['box'] = box
        _dict['num_lobes'] = 5
        _dict['num_points'] = 250

        units_dict = dict()
        units_dict['x'] = "mm"
        units_dict['y'] = "mm"

        gen = LissajousGenerator.from_dict(_dict)

        self.assertEqual(["x", "y"], gen.names)
        self.assertEqual(["x_y_Lissajous"], gen.index_names)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual(5, gen.x_freq)
        self.assertEqual(0.5, gen.x_max)
        self.assertEqual(1.0, gen.y_max)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(250, gen.num)

if __name__ == "__main__":
    unittest.main()
