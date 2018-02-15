import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from test_util import ScanPointGeneratorTest
from scanpointgenerator import PowerTermGenerator


class PowerGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        odd_pos = PowerTermGenerator("x", "mm", 0, 5, 2.5, 3, 1)
        self.assertEqual(odd_pos.units, dict(x="mm"))
        self.assertEquals(odd_pos.sign, 1)
        self.assertEquals(odd_pos.xc, 1.3572088082974532)
        self.assertEquals(odd_pos.size, 2)

        odd_neg = PowerTermGenerator("x", "mm", 5, 0, 2.5, 3, 1)
        self.assertEquals(odd_neg.sign, -1)
        self.assertEquals(odd_neg.xc, 1.3572088082974532)
        self.assertEquals(odd_neg.size, 2)

        even_pos = PowerTermGenerator("x", "mm", 4, 5, 2.5, 2, 1)
        self.assertEquals(even_pos.sign, 1)
        self.assertEquals(even_pos.xc, 1.2247448713915889)
        self.assertEquals(even_pos.size, 2)

        even_neg = PowerTermGenerator("x", "mm", 2, 0, 2.5, 2, 1)
        self.assertEquals(even_neg.sign, -1)
        self.assertEquals(even_neg.xc, 0.70710678118654757)
        self.assertEquals(even_neg.size, 2)

    def test_positions_odd_positive(self):
        gen = PowerTermGenerator("x", "mm", 260., 360., 280., 3, 10)

        expected = [260.,          262.12998637,  264.10310768,  265.92536394,
                    267.60275514,  269.14128128,  270.54694237,  271.8257384,
                    272.98366937,  274.02673528,  274.96093614,  275.79227194,
                    276.52674269,  277.17034837,  277.729089,    278.20896458,
                    278.61597509,  278.95612055,  279.23540095,  279.4598163,
                    279.63536658,  279.76805182,  279.86387199,  279.92882711,
                    279.96891717,  279.99014217,  279.99850211,  279.999997,
                    280.00062683,  280.00639161,  280.02329133,  280.05732599,
                    280.11449559,  280.20080014,  280.32223963,  280.48481406,
                    280.69452344,  280.95736776,  281.27934702,  281.66646122,
                    282.12471037,  282.66009446,  283.2786135,   283.98626747,
                    284.78905639,  285.69298026,  286.70403906,  287.82823281,
                    289.0715615,   290.44002514,  291.93962371,  293.57635724,
                    295.3562257,   297.28522911,  299.36936746,  301.61464075,
                    304.02704899,  306.61259216,  309.37727029,  312.32708335,
                    315.46803136,  318.80611431,  322.3473322,   326.09768504,
                    330.06317282,  334.24979554,  338.66355321,  343.31044582,
                    348.19647337,  353.32763587]
        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_odd_negative(self):
        gen = PowerTermGenerator('x', 'mm', 360., 260, 280, 3, 5)

        expected = [360.,          349.36925112,  339.7246309,   331.01813933,
                    323.20177641,  316.22754214,  310.04743652,  304.61345955,
                    299.87761123,  295.79189157,  292.30830055,  289.37883819,
                    286.95550448,  284.99029942,  283.43522301,  282.24227525,
                    281.36345614,  280.75076569,  280.35620388,  280.13177073,
                    280.02946623,  280.00129038,  279.99924318,  279.97532463,
                    279.88153473,  279.66987349,  279.29234089,  278.70093695,
                    277.84766166,  276.68451502,  275.16349703,  273.23660769,
                    270.855847,    267.97321496,  264.54071158]

        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_even_negative(self):
        gen = PowerTermGenerator('x', 'mm', 0., 0., 100, 2, 2.)

        expected = [0.,      9.75,    19.,     27.75,   36.,     43.75,   51.,
                    57.75,   64.,     69.75,   75.,     79.75,   84.,     87.75,
                    91.,     93.75,   96.,     97.75,   99.,     99.75,   100.,
                    99.75,   99.,     97.75,   96.,     93.75,   91.,     87.75,
                    84.,     79.75,   75.,     69.75,   64.,     57.75,   51.,
                    43.75,   36.,     27.75,   19.,     9.75]
        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_even_negative_start_bigger_than_stop(self):
        gen = PowerTermGenerator('x', 'mm', 25, 15, 40, 6, 5)

        expected = [25.,          33.3760362,   37.42933483,  39.16487299,
                    39.79089816,  39.96555244,  39.99741684,  39.9999755,
                    40.,          39.99985357,  39.9937154,   39.93772487,
                    39.67404583,  38.80885084,  36.54422547,  31.4639925]

        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_even_positive(self):
        gen = PowerTermGenerator('x', 'mm', 100., 100., 0, 2, 2.)

        expected = [100.,   90.25,   81.,     72.25,   64.,     56.25,   49.,
                    42.25,  36.,     30.25,   25.,     20.25,   16.,     12.25,
                    9.,     6.25,    4.,      2.25,    1.,      0.25,    0.,
                    0.25,   1.,      2.25,    4.,      6.25,    9.,      12.25,
                    16.,    20.25,   25.,     30.25,   36.,     42.25,   49.,
                    56.25,  64.,     72.25,   81.,     90.25]
        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_even_end_at_focus(self):
        gen = PowerTermGenerator('x', 'mm', 100., 0., 0, 2, 2.)

        expected = [100.,    90.25,   81.,     72.25,   64.,     56.25,   49.,
                    42.25,   36.,     30.25,   25.,     20.25,   16.,     12.25,
                    9.,      6.25,    4.,      2.25,    1.,      0.25]
        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_positions_even_start_at_focus(self):
        gen = PowerTermGenerator('x', 'mm', 0., 100., 0, 2, 2.)

        expected = [0.,     0.25,   1.,     2.25,   4.,     6.25,   9.,    12.25,
                    16.,    20.25,  25.,    30.25,  36.,    42.25,  49.,   56.25,
                    64.,    72.25,  81.,    90.25]
        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    def test_zero_divisor_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 5, 3, 0.)

    def test_invalid_parameters1(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 100, 50, 2, 1)

    def test_invalid_parameters2(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 100, 0, 50, 2, 1)

    def test_fractional_exponent_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 10, 3.5, 1)

    def test_negative_exponent_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 10, -5, 1)

    def test_to_dict(self):
        g = PowerTermGenerator('energy', 'eV', 260., 350., 280., 3, 5)
        expected = dict()
        expected['typeid'] = "scanpointgenerator:generator/PowerTermGenerator:1.0"
        expected['axes'] = ['energy']
        expected['units'] = "eV"
        expected['start'] = 260.
        expected['stop'] = 350.
        expected['focus'] = 280.
        expected['exponent'] = 3
        expected['divisor'] = 5.

        self.assertEquals(g.to_dict(), expected)

    def test_from_dict(self):
        _dict = dict()
        _dict['axes'] = "x"
        _dict['units'] = "cm"
        _dict['start'] = 270.
        _dict['stop'] = 500.
        _dict['focus'] = 280.
        _dict['exponent'] = 3
        _dict['divisor'] = 20.5

        units_dict = dict()
        units_dict['x'] = "cm"

        gen = PowerTermGenerator.from_dict(_dict)

        self.assertEqual(gen.axes, ["x"])
        self.assertEqual(gen.units, units_dict)
        self.assertEqual(gen.start, 270.)
        self.assertEqual(gen.stop, 500.)
        self.assertEqual(gen.focus, 280.)
        self.assertEqual(gen.exponent, 3)
        self.assertEqual(gen.divisor, 20.5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
