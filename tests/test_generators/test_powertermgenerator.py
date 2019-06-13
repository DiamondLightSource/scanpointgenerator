import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from test_util import ScanPointGeneratorTest
from scanpointgenerator import PowerTermGenerator


def _get_gen(start, stop, focus, exponent):
    return PowerTermGenerator('x', 'mm', start, stop, focus, exponent, 1)


class PowerGeneratorTest(ScanPointGeneratorTest):

    def test_axis_and_units(self):
        gen = _get_gen(0, 100, 20, 3)
        self.assertEqual(gen.units, dict(x="mm"))

    def test_array_positions(self):
        # We only need to test positions for one set of parameters
        # as long as we can reliably find the sign, xf and size
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
                    348.19647337,  353.32763587,  358.7099333]

        gen.prepare_positions()
        self.assertListAlmostEqual(gen.positions['x'], expected)

    # The following 12 tests test that the equation sign, xf, and scan size
    # are correctly calculated in 12 distinct scenarios
    # (the first 6 with an odd exponent, the final 6 with an even exponent)

    def test_params1(self):
        # 1) start < focus < stop
        gen = _get_gen(0, 100, 27, 3)
        self._check_params(gen, 1, 3, 8)

    def test_params2(self):
        # 2) start < stop < focus
        gen = _get_gen(0, 26, 27, 3)
        self._check_params(gen, 1, 3, 3)

    def test_params3(self):
        # 3) focus < start < stop
        gen = _get_gen(20, 85, 12, 3)
        self._check_params(gen, 1, -2, 3)

    def test_params4(self):
        # 4) start > focus > stop
        gen = _get_gen(77, 0, 50, 3)
        self._check_params(gen, -1, 3, 7)

    def test_params5(self):
        # 5) start > stop > focus
        gen = _get_gen(27, 1, 0, 3)
        self._check_params(gen, -1, 3, 3)

    def test_params6(self):
        # 6) focus > start > stop
        gen = _get_gen(73, 0, 100, 3)
        self._check_params(gen, -1, -3, 2)

    def test_params7(self):
        # 7) focus < start < stop
        gen = _get_gen(9, 8, 0, 2)
        self._check_params(gen, 1, 3, 6)

    def test_params8(self):
        # 8) focus < stop < start
        gen = _get_gen(9, 12, 0, 2)
        self._check_params(gen, 1, 3, 7)

    def test_params9(self):
        # 9) focus < start = stop
        gen = _get_gen(9, 9, 0, 2)
        self._check_params(gen, 1, 3, 7)

    def test_params10(self):
        # 10) focus > start > stop
        gen = _get_gen(2, 0, 18, 2)
        self._check_params(gen, -1, 4, 9)

    def test_params11(self):
        # 11) focus > stop > start
        gen = _get_gen(2, 4, 18, 2)
        self._check_params(gen, -1, 4, 8)

    def test_params12(self):
        # 12) focus > stop = start
        gen = _get_gen(0, 0, 9, 2)
        self._check_params(gen, -1, 3, 7)

    def _check_params(self, gen, sign, xf, size):
        self.assertEquals(gen.sign, sign)
        self.assertEquals(gen.xf, xf)
        self.assertEquals(gen.size, size)

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
        expected['alternate'] = False

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
        _dict['alternate'] = False

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

    # Argument validation tests
    def test_zero_divisor_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 5, 3, 0.)

    def test_fractional_exponent_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 10, 3.5, 1)

    def test_negative_exponent_raises(self):
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 10, 10, -5, 1)

    def test_invalid_parameters1(self):
        # even exponent and start < focus < stop
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 0, 100, 50, 2, 1)

    def test_invalid_parameters2(self):
        # even exponent and start > focus > stop
        with self.assertRaises(ValueError):
            PowerTermGenerator('x', 'mm', 100, 0, 50, 2, 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
