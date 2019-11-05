import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator.compat import np
from scanpointgenerator.core.dimension import Dimension

from pkg_resources import require
require("mock")
from mock import Mock


class DimensionTests(ScanPointGeneratorTest):

    def test_init(self):
        g = Mock()
        g.axes = ["x", "y"]
        g.positions = {"x":np.array([0, 1, 2]), "y":np.array([10, 11, 12])}
        g.bounds = {"x":np.array([-0.5, 0.5, 1.5, 2.5]), "y":np.array([9.5, 10.5, 11.5, 12.5])}
        g.size = 3
        d = Dimension([g])
        d.prepare()
        self.assertEqual([g], d.generators)
        self.assertEqual([], d.excluders)
        self.assertEqual(["x", "y"], d.axes)
        self.assertEqual(g.alternate, d.alternate)
        self.assertEqual(g.size, d.size)
        self.assertEqual([2, 12], d.upper)
        self.assertEqual([0, 10], d.lower)


    def test_two_generators_init(self):
        g, h = Mock(), Mock()
        g.axes, h.axes = ["gx", "gy"], ["hx", "hy"]
        g.size, h.size = 16, 64
        g.alternate = False
        h.alternate = False
        g.positions = {"gx":np.array([0, 1, 2]), "gy":np.array([10, 11, 12])}
        g.bounds = {"gx":np.array([-0.5, 0.5, 1.5, 2.5]), "gy":np.array([9.5, 10.5, 11.5, 12.5])}
        h.positions = {"hx":np.array([0, -1, -2]), "hy":np.array([-10, -11, -12])}
        h.bounds = {"hx":np.array([0.5, -0.5, -1.5, -2.5]), "hy":np.array([-9.5, -10.5, -11.5, -12.5])}

        d = Dimension([g, h])

        self.assertEqual(False, d.alternate)
        self.assertEqual(["gx", "gy", "hx", "hy"], d.axes)
        self.assertEqual([2, 12, 0, -10], d.upper)
        self.assertEqual([0, 10, -2, -12], d.lower)


    def test_excluders_init(self):
        g1, g2, g3 = Mock(), Mock(), Mock()
        e1, e2 = Mock(), Mock()
        g1.axes, g2.axes, g3.axes = ["g1"], ["g2"], ["g3"]
        g1.size, g2.size, g3.size = 3, 4, 5
        g1.positions = {"g1":np.array([0, 1, 2])}
        g1.bounds = {"g1":np.array([-0.5, 0.5, 1.5, 2.5])}
        g2.positions = {"g2":np.array([-1, 0, 1, 2])}
        g2.bounds = {"g2":np.array([-1.5, -0.5, 0.5, 1.5, 2.5])}
        g3.positions = {"g3":np.array([-2, 0, 2, 4, 6])}
        g3.bounds = {"g3":np.array([-3, -1, 1, 3, 5, 7])}
        g1.alternate = False
        g2.alternate = False
        g3.alternate = False
        e1.axes = ["g1", "g2"]
        e2.axes = ["g2", "g3"]

        d = Dimension([g1, g2, g3], [e1, e2])

        self.assertEqual(False, d.alternate)
        self.assertEqual(["g1", "g2", "g3"], d.axes)
        self.assertEqual([0, -1, -2], d.lower)
        self.assertEqual([2, 2, 6], d.upper)


    def test_positions_non_alternate(self):
        g1, g2, g3 = Mock(), Mock(), Mock()
        g1.axes, g2.axes, g3.axes = ["g1"], ["g2"], ["g3"]
        g1.size, g2.size, g3.size = 3, 4, 5
        g1.positions = {"g1":np.array([0, 1, 2])}
        g1.bounds = {"g1":np.array([-0.5, 0.5, 1.5, 2.5])}
        g2.positions = {"g2":np.array([-1, 0, 1, 2])}
        g2.bounds = {"g2":np.array([-1.5, -0.5, 0.5, 1.5, 2.5])}
        g3.positions = {"g3":np.array([-2, 0, 2, 4, 6])}
        g3.bounds = {"g3":np.array([-3, -1, 1, 3, 5, 7])}
        g1.alternate = False
        g2.alternate = False
        g3.alternate = False
        e1, e2 = Mock(), Mock()
        e1.axes = ["g1", "g2"]
        e2.axes = ["g2", "g3"]
        m1 = np.repeat(np.array([0, 1, 0, 1, 1, 0]), 10)
        m2 = np.tile(np.array([1, 0, 0, 1, 1, 1]), 10)
        e1.create_mask.return_value = m1
        e2.create_mask.return_value = m2

        d = Dimension([g1, g2, g3], [e1, e2])
        d.prepare()

        expected_mask = m1 & m2
        expected_indices = expected_mask.nonzero()[0]
        expected_g1 = np.repeat(g1.positions["g1"], 5 * 4)[expected_indices]
        expected_g2 = np.tile(np.repeat(g2.positions["g2"], 5), 3)[expected_indices]
        expected_g3 = np.tile(g3.positions["g3"], 3*4)[expected_indices]
        self.assertEqual(expected_mask.tolist(), d.mask.tolist())
        self.assertEqual(expected_indices.tolist(), d.indices.tolist())
        self.assertEqual(expected_g1.tolist(), d.positions["g1"].tolist())
        self.assertEqual(expected_g2.tolist(), d.positions["g2"].tolist())
        self.assertEqual(expected_g3.tolist(), d.positions["g3"].tolist())


    def test_multi_axis_per_generator(self):
        g1, g2 = Mock(), Mock()
        g1.axes = ["z"]
        g2.axes = ["x", "y"]
        g1.positions = {"z":np.array([100, 200, 300, 400])}
        g1.bounds = {"z":np.array([50, 150, 250, 350, 450])}
        g2.positions = {"x":np.array([10, 11, 12]), "y":np.array([-1, -2, -3])}
        g2.bounds = {"x":np.array([9.5, 10.5, 11.5, 12.5]), "y":np.array([-0.5, -1.5, -2.5, -3.5])}
        g1.size, g2.size = 4, 3
        g1.alternate, g2.alternate = False, False
        e1, e2 = Mock(), Mock()
        e1.axes = ["x", "y"]
        e2.axes = ["x", "z"]
        m1 = np.array([1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0])
        m2 = np.array([1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1])
        e1.create_mask.return_value = m1
        e2.create_mask.return_value = m2

        d = Dimension([g1, g2], [e1, e2])
        d.prepare()

        expected_mask = m1 & m2
        expected_indices = expected_mask.nonzero()[0]
        expected_x = [10, 10, 11, 11]
        expected_y = [-1, -1, -2, -2]
        expected_z = [100, 300, 300, 400]
        self.assertEqual(4, d.size)
        self.assertEqual(expected_mask.tolist(), d.mask.tolist())
        self.assertEqual(expected_indices.tolist(), d.indices.tolist())
        self.assertEqual(expected_x, d.positions["x"].tolist())
        self.assertEqual(expected_y, d.positions["y"].tolist())
        self.assertEqual(expected_z, d.positions["z"].tolist())


    def test_single_alternating_generator_with_excluder(self):
        x_pos = np.array([0, 1, 2, 3, 4, 5])
        x_bounds = np.array([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        y_bounds = np.array([9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5])
        g = Mock(
                axes=["x", "y"],
                positions={"x":x_pos, "y":y_pos},
                bounds={"x":x_bounds, "y":y_bounds},
                size=6)
        g.alternate = True
        mask = np.array([1, 1, 0, 1, 0, 0], dtype=np.int8)
        e = Mock(axes=["x", "y"], create_mask=Mock(return_value=mask))

        d = Dimension([g], [e])

        self.assertTrue(d.alternate)

        d.prepare()

        expected_x = [0, 1, 3]
        expected_y = [10, 11, 13]
        self.assertEqual(expected_x, d.positions["x"].tolist())
        self.assertEqual(expected_y, d.positions["y"].tolist())


    def test_positions_alternating(self):
        g1, g2 = Mock(), Mock()
        g1.axes = ["z"]
        g2.axes = ["x", "y"]
        g1.positions = {"z":np.array([100, 200, 300, 400])}
        g1.bounds = {"z":np.array([50, 150, 250, 350, 450])}
        g2.positions = {"x":np.array([10, 11, 12]), "y":np.array([-1, -2, -3])}
        g2.bounds = {"x":np.array([9.5, 10.5, 11.5, 12.5]), "y":np.array([-0.5, -1.5, -2.5, -3.5])}
        g1.size, g2.size = 4, 3
        g1.alternate, g2.alternate = False, True
        e1, e2 = Mock(), Mock()
        e1.axes = ["x", "y"]
        e2.axes = ["x", "z"]
        m1 = np.array([1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1])
        m2 = np.array([1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1])
        e1.create_mask.return_value = m1
        e2.create_mask.return_value = m2

        d = Dimension([g1, g2], [e1, e2])
        d.prepare()

        expected_mask = m1 & m2
        expected_indices = expected_mask.nonzero()[0]
        expected_x = [10, 11, 12, 11, 12, 11, 10]
        expected_y = [-1, -2, -3, -2, -3, -2, -1]
        expected_z = [100, 100, 200, 200, 300, 400, 400]
        self.assertEqual(7, d.size)
        self.assertEqual(expected_mask.tolist(), d.mask.tolist())
        self.assertEqual(expected_indices.tolist(), d.indices.tolist())
        self.assertEqual(expected_x, d.positions["x"].tolist())
        self.assertEqual(expected_y, d.positions["y"].tolist())
        self.assertEqual(expected_z, d.positions["z"].tolist())


    def test_single_axis_excluder(self):
        x_pos = np.array([0, 1, 2, 3, 4, 5])
        x_bounds = np.array([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        y_bounds = np.array([9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5])
        g = Mock(axes=["x", "y"],
                positions={"x":x_pos, "y":y_pos},
                bounds={"x":x_bounds, "y":y_bounds},
                size=len(x_pos))
        g.alternate = False
        e = Mock(axes=["x"], create_mask=lambda x: (2 <= x) & (x < 4) | (x == 5))
        d = Dimension([g], [e])
        d.prepare()

        self.assertEqual([2, 3, 5], d.get_positions('x').tolist())
        self.assertEqual([12, 13, 15], d.get_positions('y').tolist())


    def test_excluder_over_spread_axes(self):
        gw_pos = np.array([0.1, 0.2])
        gw_bounds = np.array([0.05, 0.15, 0.25])
        gx_pos = np.array([0, 1, 2, 3])
        gy_pos = np.array([10, 11, 12, 13])
        gz_pos = np.array([100, 101, 102, 103])
        go_pos = np.array([1000, 1001, 1002])
        mask_xz_func = lambda px, pz: (px-1)**2 + (pz-102)**2 <= 1
        exz = Mock(axes=["gx", "gz"], create_mask=Mock(side_effect=mask_xz_func))
        gw = Mock(axes=["gw"], positions={"gw":gw_pos}, bounds={"gw":gw_bounds}, size=2, alternate=False)
        gx = Mock(axes=["gx"], positions={"gx":gx_pos}, size=4, alternate=False)
        gy = Mock(axes=["gy"], positions={"gy":gy_pos}, size=4, alternate=False)
        gz = Mock(axes=["gz"], positions={"gz":gz_pos}, size=4, alternate=False)
        go = Mock(axes=["go"], positions={"go":go_pos}, size=3, alternate=False)

        d = Dimension([go, gz, gy, gx, gw], [exz])
        d.prepare()

        x_positions = np.tile(np.array([0, 1, 2, 3]), 16)
        y_positions = np.repeat(np.tile(np.array([10, 11, 12, 13]), 4), 4)
        z_positions = np.repeat(np.array([100, 101, 102, 103]), 16)
        x_positions = np.tile(np.repeat(x_positions, gw.size), go.size)
        y_positions = np.tile(np.repeat(y_positions, gw.size), go.size)
        z_positions = np.tile(np.repeat(z_positions, gw.size), go.size)

        mask = mask_xz_func(x_positions, z_positions)
        expected_x = x_positions[mask].tolist()
        expected_y = y_positions[mask].tolist()
        expected_z = z_positions[mask].tolist()

        self.assertEqual(expected_x, d.get_positions("gx").tolist())
        self.assertEqual(expected_y, d.get_positions("gy").tolist())
        self.assertEqual(expected_z, d.get_positions("gz").tolist())


    def test_spread_excluder_multi_axes_per_gen(self):
        gx1_pos = np.array([1, 2, 3, 4, 5])
        gx1_bounds = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
        gx2_pos = np.array([11, 10, 9, 8, 7])
        gx2_bounds = np.array([11.5, 10.5, 9.5, 8.5, 7.5, 6.5])
        gy_pos = np.array([-1, 0, 1])
        gz_pos = np.array([1, 0, -1, -2, -3])
        mask_x1z_func = lambda px, pz: (px-4)**2 + (pz+1)**2 <= 1
        exz = Mock(axes=["gx1", "gz"], create_mask=Mock(side_effect=mask_x1z_func))
        gx = Mock(axes=["gx1", "gx2"],
                positions={"gx1":gx1_pos, "gx2":gx2_pos},
                bounds={"gx1":gx1_bounds, "gx2":gx2_bounds},
                size=5, alternate=False)
        gy = Mock(axes=["gy"], positions={"gy":gy_pos}, size=3, alternate=False)
        gz = Mock(axes=["gz"], positions={"gz":gz_pos}, size=5, alternate=False)
        d = Dimension([gz, gy, gx], [exz])

        d.prepare()

        x1_positions = np.tile(gx1_pos, 15)
        x2_positions = np.tile(gx2_pos, 15)
        y_positions = np.repeat(np.tile(gy_pos, 5), 5)
        z_positions = np.repeat(gz_pos, 15)

        mask = mask_x1z_func(x1_positions, z_positions)
        expected_x1 = x1_positions[mask].tolist()
        expected_x2 = x2_positions[mask].tolist()
        expected_y = y_positions[mask].tolist()
        expected_z = z_positions[mask].tolist()

        self.assertEqual(expected_x1, d.get_positions("gx1").tolist())
        self.assertEqual(expected_x2, d.get_positions("gx2").tolist())
        self.assertEqual(expected_y, d.get_positions("gy").tolist())
        self.assertEqual(expected_z, d.get_positions("gz").tolist())


    def test_high_dimensional_excluder(self):
        w_pos = np.array([0, 1, 2, 3, 4, 5])
        w_bounds = np.array([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
        x_pos = np.array([0, 1, 2, 3, 4, 5])
        y_pos = np.array([0, 1, 2, 3, 4, 5])
        z_pos = np.array([0, 1, 2, 3, 4, 5])
        mask_function = lambda pw, px, py, pz: (pw-2)**2 + (px-2)**2 + (py-1)**2 + (pz-3)**2 <= 1.1
        excluder = Mock(axes=["w", "x", "y", "z"], create_mask=Mock(side_effect=mask_function))
        gw = Mock(axes=["w"], positions={"w":w_pos}, bounds={"w":w_bounds}, size=len(w_pos), alternate=False)
        gx = Mock(axes=["x"], positions={"x":x_pos}, size=len(x_pos), alternate=False)
        gy = Mock(axes=["y"], positions={"y":y_pos}, size=len(y_pos), alternate=False)
        gz = Mock(axes=["z"], positions={"z":z_pos}, size=len(z_pos), alternate=False)
        d = Dimension([gz, gy, gx, gw], [excluder])

        d.prepare()

        w_positions = np.tile(w_pos, len(x_pos) * len(y_pos) * len(z_pos))
        x_positions = np.repeat(np.tile(x_pos, len(y_pos) * len(z_pos)), len(w_pos))
        y_positions = np.repeat(np.tile(y_pos, len(z_pos)), len(w_pos) * len(x_pos))
        z_positions = np.repeat(z_pos, len(w_pos) * len(x_pos) * len(y_pos))
        mask = mask_function(w_positions, x_positions, y_positions, z_positions)
        w_expected = w_positions[mask].tolist()
        x_expected = x_positions[mask].tolist()
        y_expected = y_positions[mask].tolist()
        z_expected = z_positions[mask].tolist()

        self.assertEqual(w_expected, d.get_positions("w").tolist())
        self.assertEqual(x_expected, d.get_positions("x").tolist())
        self.assertEqual(y_expected, d.get_positions("y").tolist())
        self.assertEqual(z_expected, d.get_positions("z").tolist())


    def test_get_mesh_map(self):
        # Set up a generator, with 3x4 grid with alternating x and a circular
        # excluder such that the four 'corners' of the grid are excluded
        gx_pos = np.array([0.1, 0.2, 0.3])
        gx_bounds = np.array([0.05, 0.15, 0.25, 0.35])
        gy_pos = np.array([1.1, 1.2, 1.3, 1.4])
        mask_func = lambda px, py: (px - 0.2) ** 2 + (py - 1.25) ** 2 <= 0.0225
        gx = Mock(axes=["gx"], positions={"gx": gx_pos}, bounds={"gx":gx_bounds}, size=3,
                  alternate=True)
        gy = Mock(axes=["gy"], positions={"gy": gy_pos}, size=4,
                  alternate=False)
        e = Mock(axes=["gx", "gy"], create_mask=Mock(side_effect=mask_func))

        d = Dimension([gy, gx], [e])
        d.prepare()

        self.assertEqual([1, 2, 1, 0, 0, 1, 2, 1],
                         d.get_mesh_map("gx").tolist())
        self.assertEqual([0, 1, 1, 1, 2, 2, 2, 3],
                         d.get_mesh_map("gy").tolist())


    def test_mixed_alternating_generators(self):
        x_pos = np.array([0, 1, 2])
        x_bounds = np.array([-0.5, 0.5, 1.5, 2.5])
        y_pos = np.array([10, 11, 12])
        z_pos = np.array([20, 21, 22])
        w_pos = np.array([30, 31, 32])
        gx = Mock(axes=["x"], positions={"x":x_pos}, bounds={"x":x_bounds}, size=3, alternate=True)
        gy = Mock(axes=["y"], positions={"y":y_pos}, size=3, alternate=True)
        gz = Mock(axes=["z"], positions={"z":z_pos}, size=3, alternate=False)
        gw = Mock(axes=["w"], positions={"w":w_pos}, size=3, alternate=False)

        mask = np.array([1, 1, 0, 1, 1, 1, 1, 0, 1] * 9)
        indices = np.nonzero(mask)[0]
        e = Mock(axes=["x", "y", "z", "w"])
        e.create_mask.return_value=mask

        d = Dimension([gw, gz, gy, gx], [e])
        d.prepare()

        expected_x = np.append(np.tile(np.append(x_pos, x_pos[::-1]), 13), x_pos)[indices]
        expected_y = np.repeat(np.append(np.tile(np.append(y_pos, y_pos[::-1]), 4), y_pos), 3)[indices]
        expected_z = np.tile(np.repeat(z_pos, 9), 3)[indices]
        expected_w = np.repeat(w_pos, 27)[indices]
        self.assertEqual(False, d.alternate)
        self.assertEqual(expected_x.tolist(), d.get_positions("x").tolist())
        self.assertEqual(expected_y.tolist(), d.get_positions("y").tolist())
        self.assertEqual(expected_z.tolist(), d.get_positions("z").tolist())
        self.assertEqual(expected_w.tolist(), d.get_positions("w").tolist())


    def test_dim_alternate_condition(self):
        g1 = Mock(
                axes=["x"],
                positions={"x":np.array([1, 2, 3])},
                bounds={"x":np.array([0.5, 1.5, 2.5, 3.5])},
                size=3,
                alternate=True)
        g2 = Mock(
                axes=["y"],
                positions={"y":np.array([1, 2, 3])},
                bounds={"y":np.array([0.5, 1.5, 2.5, 3.5])},
                size=3,
                alternate=False)
        g3 = Mock(
                axes=["z"],
                positions={"z":np.array([1, 2, 3])},
                bounds={"z":np.array([0.5, 1.5, 2.5, 3.5])},
                size=3,
                alternate=True)

        d1 = Dimension([g1, g3])
        d2 = Dimension([g2, g3])
        self.assertEqual(True, d1.alternate)
        self.assertEqual(False, d2.alternate)

        d1.prepare()
        d2.prepare()
        self.assertEqual(True, d1.alternate)
        self.assertEqual(False, d2.alternate)


    def test_dim_invalid_alternating(self):
        g1 = Mock(
                axes=["x"],
                positions={"x":np.array([1, 2, 3])},
                bounds={"x":np.array([0.5, 1.5, 2.5, 3.5])},
                size=3,
                alternate=True)
        g2 = Mock(
                axes=["y"],
                positions={"y":np.array([1, 2, 3])},
                bounds={"y":np.array([0.5, 1.5, 2.5, 3.5])},
                size=3,
                alternate=False)

        with self.assertRaises(ValueError):
            d = Dimension([g1, g2])



if __name__ == "__main__":
    unittest.main(verbosity=2)
