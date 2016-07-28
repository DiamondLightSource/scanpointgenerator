from collections import OrderedDict
import unittest

from scanpointgenerator import SpiralGenerator


class SpiralGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.g = SpiralGenerator("XYSpiral", "mm", [0.0, 0.0], 1.4, alternate_direction=True)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(XYSpiral_X="mm", XYSpiral_Y="mm"))
        self.assertEqual(self.g.index_dims, [6])
        self.assertEqual(self.g.index_names, ["XYSpiral"])

    def test_iterator(self):
        positions = [{'XYSpiral_Y': -0.3211855677650875,
                      'XYSpiral_X': 0.23663214944574582},
                     {'XYSpiral_Y': -0.25037538922751695,
                      'XYSpiral_X': -0.6440318266552169},
                     {'XYSpiral_Y': 0.6946549630820702,
                      'XYSpiral_X': -0.5596688286164636},
                     {'XYSpiral_Y': 0.9919687803189761,
                      'XYSpiral_X': 0.36066957248394327},
                     {'XYSpiral_Y': 0.3924587351155914,
                      'XYSpiral_X': 1.130650533568409},
                     {'XYSpiral_Y': -0.5868891557832875,
                      'XYSpiral_X': 1.18586065489788},
                     {'XYSpiral_Y': -1.332029488076613,
                      'XYSpiral_X': 0.5428735608675326}]
        lower = [{'XYSpiral_Y': 0.0, 'XYSpiral_X': 0.0},
                 {'XYSpiral_Y': -0.5189218293602549,
                  'XYSpiral_X': -0.2214272368007088},
                 {'XYSpiral_Y': 0.23645222432582483,
                  'XYSpiral_X': -0.7620433832656455},
                 {'XYSpiral_Y': 0.9671992383675001,
                  'XYSpiral_X': -0.13948222773063082},
                 {'XYSpiral_Y': 0.7807653675717078,
                  'XYSpiral_X': 0.8146440851904461},
                 {'XYSpiral_Y': -0.09160107657707395,
                  'XYSpiral_X': 1.2582363345925418},
                 {'XYSpiral_Y': -1.0190886264001306,
                  'XYSpiral_X': 0.9334439933089926}]
        upper = [{'XYSpiral_Y': -0.5189218293602549,
                  'XYSpiral_X': -0.2214272368007088},
                 {'XYSpiral_Y': 0.23645222432582483,
                  'XYSpiral_X': -0.7620433832656455},
                 {'XYSpiral_Y': 0.9671992383675001,
                  'XYSpiral_X': -0.13948222773063082},
                 {'XYSpiral_Y': 0.7807653675717078,
                  'XYSpiral_X': 0.8146440851904461},
                 {'XYSpiral_Y': -0.09160107657707395,
                  'XYSpiral_X': 1.2582363345925418},
                 {'XYSpiral_Y': -1.0190886264001306,
                  'XYSpiral_X': 0.9334439933089926},
                 {'XYSpiral_Y': -1.4911377166541206,
                  'XYSpiral_X': 0.06839234794968006}]
        indexes = [0, 1, 2, 3, 4, 5, 6]

        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, positions[i])
            self.assertEqual(p.lower, lower[i])
            self.assertEqual(p.upper, upper[i])
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 6)

    def test_to_dict(self):
        expected_dict = OrderedDict()
        expected_dict['type'] = "SpiralGenerator"
        expected_dict['name'] = "XYSpiral"
        expected_dict['units'] = 'mm'
        expected_dict['centre'] = [0.0, 0.0]
        expected_dict['radius'] = 1.4
        expected_dict['scale'] = 1
        expected_dict['alternate_direction'] = True

        d = self.g.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = OrderedDict()
        _dict['type'] = "SpiralGenerator"
        _dict['name'] = "XYSpiral"
        _dict['units'] = "mm"
        _dict['centre'] = [0.0, 0.0]
        _dict['radius'] = 1.4
        _dict['scale'] = 1
        _dict['alternate_direction'] = True

        units_dict = OrderedDict()
        units_dict['XYSpiral_X'] = "mm"
        units_dict['XYSpiral_Y'] = "mm"

        gen = SpiralGenerator.from_dict(_dict)

        self.assertEqual("XYSpiral", gen.name)
        self.assertEqual(units_dict, gen.position_units)
        self.assertEqual([0.0, 0.0], gen.centre)
        self.assertEqual(1.4, gen.radius)
        self.assertEqual(1, gen.scale)
