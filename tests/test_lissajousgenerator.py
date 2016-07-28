from collections import OrderedDict
import unittest

from scanpointgenerator import LissajousGenerator


class LissajousGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
        self.g = LissajousGenerator("XYLissajous", "mm", self.bounding_box, 1)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(XYLissajous_X="mm", XYLissajous_Y="mm"))
        self.assertEqual(self.g.index_dims, [250])
        self.assertEqual(self.g.index_names, ["XYLissajous"])

    def test_iterator(self):
        g = LissajousGenerator("XYLissajous", "mm", self.bounding_box, 1, num_points=10)
        positions = [{'XYLissajous_Y': 0.0, 'XYLissajous_X': 0.5},
                     {'XYLissajous_Y': 0.47552825814757677,
                      'XYLissajous_X': 0.4045084971874737},
                     {'XYLissajous_Y': 0.2938926261462366,
                      'XYLissajous_X': 0.15450849718747375},
                     {'XYLissajous_Y': -0.2938926261462365,
                      'XYLissajous_X': -0.15450849718747364},
                     {'XYLissajous_Y': -0.4755282581475768,
                      'XYLissajous_X': -0.40450849718747367},
                     {'XYLissajous_Y': -1.2246467991473532e-16,
                      'XYLissajous_X': -0.5},
                     {'XYLissajous_Y': 0.47552825814757677,
                      'XYLissajous_X': -0.4045084971874738},
                     {'XYLissajous_Y': 0.2938926261462367,
                      'XYLissajous_X': -0.1545084971874738},
                     {'XYLissajous_Y': -0.2938926261462364,
                      'XYLissajous_X': 0.1545084971874736},
                     {'XYLissajous_Y': -0.4755282581475769,
                      'XYLissajous_X': 0.4045084971874736}]
        lower = [{'XYLissajous_Y': -0.29389262614623657,
                  'XYLissajous_X': 0.47552825814757677},
                 {'XYLissajous_Y': 0.29389262614623657,
                  'XYLissajous_X': 0.4755282581475768},
                 {'XYLissajous_Y': 0.4755282581475768,
                  'XYLissajous_X': 0.2938926261462366},
                 {'XYLissajous_Y': 6.123233995736766e-17,
                  'XYLissajous_X': 6.123233995736766e-17},
                 {'XYLissajous_Y': -0.47552825814757677,
                  'XYLissajous_X': -0.2938926261462365},
                 {'XYLissajous_Y': -0.2938926261462367,
                  'XYLissajous_X': -0.47552825814757677},
                 {'XYLissajous_Y': 0.29389262614623646,
                  'XYLissajous_X': -0.4755282581475768},
                 {'XYLissajous_Y': 0.4755282581475768,
                  'XYLissajous_X': -0.2938926261462367},
                 {'XYLissajous_Y': 1.8369701987210297e-16,
                  'XYLissajous_X': -1.2246467991473532e-16},
                 {'XYLissajous_Y': -0.4755282581475767,
                  'XYLissajous_X': 0.29389262614623646}]
        upper = [{'XYLissajous_Y': 0.29389262614623657,
                  'XYLissajous_X': 0.4755282581475768},
                 {'XYLissajous_Y': 0.4755282581475768,
                  'XYLissajous_X': 0.2938926261462366},
                 {'XYLissajous_Y': 6.123233995736766e-17,
                  'XYLissajous_X': 6.123233995736766e-17},
                 {'XYLissajous_Y': -0.47552825814757677,
                  'XYLissajous_X': -0.2938926261462365},
                 {'XYLissajous_Y': -0.2938926261462367,
                  'XYLissajous_X': -0.47552825814757677},
                 {'XYLissajous_Y': 0.29389262614623646,
                  'XYLissajous_X': -0.4755282581475768},
                 {'XYLissajous_Y': 0.4755282581475768,
                  'XYLissajous_X': -0.2938926261462367},
                 {'XYLissajous_Y': 1.8369701987210297e-16,
                  'XYLissajous_X': -1.2246467991473532e-16},
                 {'XYLissajous_Y': -0.4755282581475767,
                  'XYLissajous_X': 0.29389262614623646},
                 {'XYLissajous_Y': -0.29389262614623674,
                  'XYLissajous_X': 0.47552825814757677}]
        indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        for i, p in enumerate(g.iterator()):
            self.assertEqual(p.positions, positions[i])
            self.assertEqual(p.lower, lower[i])
            self.assertEqual(p.upper, upper[i])
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 9)

    def test_to_dict(self):
        expected_dict = OrderedDict()
        box = OrderedDict()
        expected_dict['type'] = "LissajousGenerator"
        box['centre'] = [0.0, 0.0]
        box['width'] = 1.0
        box['height'] = 1.0

        expected_dict['name'] = "XYLissajous"
        expected_dict['units'] = "mm"
        expected_dict['box'] = box
        expected_dict['num_lobes'] = 1
        expected_dict['num_points'] = 250

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        box = OrderedDict()
        box['centre'] = [0.0, 0.0]
        box['width'] = 1.0
        box['height'] = 2.0

        _dict = OrderedDict()
        _dict['name'] = "XYLissajous"
        _dict['units'] = "mm"
        _dict['box'] = box
        _dict['num_lobes'] = 5
        _dict['num_points'] = 250

        units_dict = OrderedDict()
        units_dict['XYLissajous_X'] = "mm"
        units_dict['XYLissajous_Y'] = "mm"

        gen = LissajousGenerator.from_dict(_dict)

        self.assertEqual("XYLissajous", gen.name)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual(5, gen.x_freq)
        self.assertEqual(0.5, gen.x_max)
        self.assertEqual(1.0, gen.y_max)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(250, gen.num)
