import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.compat import range_
from scanpointgenerator.mutators import RotationMutator
from scanpointgenerator import Point

from pkg_resources import require
require("mock")
from mock import MagicMock

float_error_tolerance = 1e-12

def make_point(j,k):
    pt = Point()
    pt.indexes = [j, k]
    if k == 9:
        pt.positions = {"x": j / 10., "y": k / 10.}
        pt.lower = {"x": j / 10., "y": (k - 0.5) / 10.}
        pt.upper = {"x": (j + 0.5) / 10., "y": 0.45}
    elif k == 0:
        pt.positions = {"x": j / 10., "y": k / 10.}
        pt.lower = {"x": (j - 0.5) / 10., "y": 0.45}
        pt.upper = {"x": j / 10., "y": (k + 0.5) / 10.}
    else:
        pt.positions = {"x": j / 10., "y": k / 10.}
        pt.lower = {"x": j / 10., "y": (k - 0.5) / 10.}
        pt.upper = {"x": j / 10., "y": (k + 0.5) / 10.}
    return pt

class RotationMutatorTest(ScanPointGeneratorTest):

    def test_init(self):
        m = RotationMutator(["x", "y"], 30, [0., 0.])
        self.assertEqual(30, m.angle)

    def test_init_fails_for_invalid_axes(self):
        self.assertRaises(AssertionError, RotationMutator, ["x"], 30, [0.])
        self.assertRaises(AssertionError, RotationMutator, ["x", "y", "z"], 30, [0., 0., 0.])

    def test_mutate_simple(self):
        def point_gen():
            for j in range_(10):
                for k in range_(10):
                    pt = make_point(j, k)
                    yield pt
        m = RotationMutator(["x", "y"], 30, [0., 0.])
        original = [p for p in point_gen()]
        mutated = [m.mutate(p, i) for i, p in enumerate(point_gen())]
        for o, m in zip(original, mutated):
            op_x, mp_x = o.positions["x"], m.positions["x"]
            op_y, mp_y = o.positions["y"], m.positions["y"]
            ou_x, mu_x = o.upper["x"], m.upper["x"]
            ou_y, mu_y = o.upper["y"], m.upper["y"]
            ol_x, ml_x = o.lower["x"], m.lower["x"]
            ol_y, ml_y = o.lower["y"], m.lower["y"]
            self.assertTrue(abs((op_x**2 + op_y**2) - (mp_x**2 + mp_y**2)) < float_error_tolerance)

        for i in range(len(original) - 1):
            # check distance between consecutive points is preserved
            o_step = (original[i + 1].positions["x"] - original[i].positions["x"]) ** 2 + \
                     (original[i + 1].positions["y"] - original[i].positions["y"]) ** 2
            m_step = (mutated[i + 1].positions["x"] - mutated[i].positions["x"]) ** 2 + \
                     (mutated[i + 1].positions["y"] - mutated[i].positions["y"]) ** 2
            self.assertTrue(abs(o_step - m_step) < float_error_tolerance)

            # check angle between points preserved
            o_dot = (original[i + 1].positions["x"] * original[i].positions["x"]) + \
                    (original[i + 1].positions["y"] * original[i].positions["y"])
            m_dot = (mutated[i + 1].positions["x"] * mutated[i].positions["x"]) + \
                    (mutated[i + 1].positions["y"] * mutated[i].positions["y"])
            self.assertTrue(abs(o_dot - m_dot) < float_error_tolerance)

            # check bounds still correct
            self.assertEqual(original[i + 1].lower["x"], original[i].upper["x"])
            self.assertEqual(original[i + 1].lower["y"], original[i].upper["y"])
            self.assertEqual(mutated[i + 1].lower["x"], mutated[i].upper["x"])
            self.assertEqual(mutated[i + 1].lower["y"], mutated[i].upper["y"])

    def test_mutate_cor(self):
        def point_gen():
            for j in range_(10):
                for k in range_(10):
                    pt = make_point(j, k)
                yield pt
        CoR = [2., 3.]
        m = RotationMutator(["x", "y"], 30, CoR)
        original = [p for p in point_gen()]
        mutated = [m.mutate(p, i) for i, p in enumerate(point_gen())]
        o_r = []
        m_r = []
        o_rel_x = []
        o_rel_y = []
        m_rel_x = []
        m_rel_y = []
        for o, m in zip(original, mutated):
            op_x, mp_x = o.positions["x"], m.positions["x"]
            op_y, mp_y = o.positions["y"], m.positions["y"]
            ou_x, mu_x = o.upper["x"], m.upper["x"]
            ou_y, mu_y = o.upper["y"], m.upper["y"]
            ol_x, ml_x = o.lower["x"], m.lower["x"]
            ol_y, ml_y = o.lower["y"], m.lower["y"]
            # self.assertNotEqual(op_x, mp_x)
            # self.assertNotEqual(op_y, mp_y)
            o_rel_x += [op_x - CoR[0]]
            o_rel_y += [op_y - CoR[1]]
            m_rel_x += [mp_x - CoR[0]]
            m_rel_y += [mp_y - CoR[1]]
            o_r += [(op_x - CoR[0]) ** 2 + (op_y - CoR[1]) ** 2]
            m_r += [(mp_x - CoR[0]) ** 2 + (mp_y - CoR[1]) ** 2]

            self.assertTrue(abs(m_r[-1] - o_r[-1]) < float_error_tolerance)

        for i in range(len(original) - 1):
            # check distance between consecutive points is preserved
            o_step = (original[i + 1].positions["x"] - original[i].positions["x"]) ** 2 + \
                     (original[i + 1].positions["y"] - original[i].positions["y"]) ** 2
            m_step = (mutated[i + 1].positions["x"] - mutated[i].positions["x"]) ** 2 + \
                     (mutated[i + 1].positions["y"] - mutated[i].positions["y"]) ** 2
            self.assertTrue(abs(o_step - m_step) < float_error_tolerance)

            # check angle between points preserved
            o_dot = (o_rel_x[i + 1] * o_rel_x[i]) + (o_rel_y[i + 1] * o_rel_y[i])
            m_dot = (m_rel_x[i + 1] * m_rel_x[i]) + (m_rel_y[i + 1] * m_rel_y[i])
            self.assertTrue(abs(o_dot - m_dot) < float_error_tolerance)

    def test_mutate_90_degrees(self):
        def point_gen():
            for j in range_(10):
                for k in range_(10):
                    pt = make_point(j, k)
                yield pt
        m = RotationMutator(["x", "y"], 90, [0., 0.])
        original = [p for p in point_gen()]
        mutated = [m.mutate(p, i) for i, p in enumerate(point_gen())]
        for o, m in zip(original, mutated):
            op_x, mp_x = o.positions["x"], m.positions["x"]
            op_y, mp_y = o.positions["y"], m.positions["y"]
            ou_x, mu_x = o.upper["x"], m.upper["x"]
            ou_y, mu_y = o.upper["y"], m.upper["y"]
            ol_x, ml_x = o.lower["x"], m.lower["x"]
            ol_y, ml_y = o.lower["y"], m.lower["y"]
            # self.assertNotEqual(op_x, mp_x)
            # self.assertNotEqual(op_y, mp_y)
            self.assertTrue(abs((op_x**2 + op_y**2) - (mp_x**2 + mp_y**2)) < float_error_tolerance)
            # rotate 90 degrees, mp_y = op_x, mp_x = -op_y
            self.assertTrue(abs(op_x - mp_y) < float_error_tolerance)
            self.assertTrue(abs(op_y + mp_x) < float_error_tolerance)

        # check distance between consecutive points is preserved
        for i in range(len(original) - 1):
            o_step = (original[i + 1].positions["x"] - original[i].positions["x"]) ** 2 + \
                     (original[i + 1].positions["y"] - original[i].positions["y"]) ** 2
            m_step = (mutated[i + 1].positions["x"] - mutated[i].positions["x"]) ** 2 + \
                     (mutated[i + 1].positions["y"] - mutated[i].positions["y"]) ** 2
            self.assertTrue(abs(o_step - m_step) < float_error_tolerance)

    def test_mutate_twice_opposite(self):
        def point_gen():
            for j in range_(10):
                for k in range_(10):
                    pt = make_point(j, k)
                yield pt
        m1 = RotationMutator(["x", "y"], 30, [0., 0.])
        m2 = RotationMutator(["x", "y"], -30, [0., 0.])
        original = [p for p in point_gen()]
        mutated1 = [m1.mutate(p, i) for i, p in enumerate(point_gen())]
        mutated2 = [m2.mutate(p, i) for i, p in enumerate(mutated1)]
        for o, m in zip(original, mutated2):
            op_x, mp_x = o.positions["x"], m.positions["x"]
            op_y, mp_y = o.positions["y"], m.positions["y"]
            ou_x, mu_x = o.upper["x"], m.upper["x"]
            ou_y, mu_y = o.upper["y"], m.upper["y"]
            ol_x, ml_x = o.lower["x"], m.lower["x"]
            ol_y, ml_y = o.lower["y"], m.lower["y"]
            # should be equal within floating point error
            self.assertTrue(abs(mp_x - op_x) < float_error_tolerance)
            self.assertTrue(abs(mu_x - ou_x) < float_error_tolerance)
            self.assertTrue(abs(ml_x - ol_x) < float_error_tolerance)
            self.assertTrue(abs(mp_y - op_y) < float_error_tolerance)
            self.assertTrue(abs(mu_y - ou_y) < float_error_tolerance)
            self.assertTrue(abs(ml_y - ol_y) < float_error_tolerance)


class TestSerialisation(unittest.TestCase):

    def setUp(self):
        self.l = MagicMock()
        self.l_dict = MagicMock()
        self.centreOfRotation = [0., 0.]
        self.m = RotationMutator(["x", "y"], 45, self.centreOfRotation)

    def test_to_dict(self):
        self.l.to_dict.return_value = self.l_dict

        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:mutator/RotationMutator:1.0"
        expected_dict['angle'] = 45
        expected_dict['axes'] = ["x", "y"]
        expected_dict['centreOfRotation'] = self.centreOfRotation

        d = self.m.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):

        _dict = dict()
        _dict['angle'] = 45
        _dict['axes'] = ["x", "y"]
        _dict['centreOfRotation'] = self.centreOfRotation

        units_dict = dict()
        units_dict['x'] = 'mm'
        units_dict['y'] = 'mm'

        m = RotationMutator.from_dict(_dict)

        self.assertEqual(45, m.angle)
        self.assertEqual(self.centreOfRotation, m.centreOfRotation)


if __name__ == "__main__":
    unittest.main(verbosity=2)
