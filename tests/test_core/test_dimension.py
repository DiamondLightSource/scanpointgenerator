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
        g.size = 3
        d = Dimension(g)
        d.prepare()
        self.assertEqual([g], d.generators)
        self.assertEqual(["x", "y"], d.axes)
        self.assertEqual([], d._masks)
        self.assertEqual(g.alternate, d.alternate)
        self.assertEqual(g.size, d.size)
        self.assertEqual([2, 12], d.upper)
        self.assertEqual([0, 10], d.lower)

    def test_merge_dimensions(self):
        g, h = Mock(), Mock()
        g.axes, h.axes = ["gx", "gy"], ["hx", "hy"]
        g.size, h.size = 16, 64
        g.positions = {"gx":np.array([0, 1, 2]), "gy":np.array([10, 11, 12])}
        h.positions = {"hx":np.array([0, -1, -2]), "hy":np.array([-10, -11, -12])}
        outer, inner = Dimension(g), Dimension(h)
        om1, om2 = Mock(), Mock()
        im1, im2 = Mock(), Mock()
        outer._masks = [{"repeat":2, "tile":3, "mask":om1},
            {"repeat":5, "tile":7, "mask":om2}]
        inner._masks = [{"repeat":11, "tile":13, "mask":im1},
            {"repeat":17, "tile":19, "mask":im2}]
        combined = Dimension.merge_dimensions(outer, inner)

        self.assertEqual(g.size * h.size, combined._max_length)
        self.assertEqual(outer.alternate or inner.alternate, combined.alternate)
        self.assertEqual(["gx", "gy", "hx", "hy"], combined.axes)
        self.assertEqual([2, 12, 0, -10], combined.upper)
        self.assertEqual([0, 10, -2, -12], combined.lower)
        expected_masks = [
            {"repeat":128, "tile":3, "mask":om1},
            {"repeat":320, "tile":7, "mask":om2},
            {"repeat":11, "tile":13*16, "mask":im1},
            {"repeat":17, "tile":19*16, "mask":im2}]
        self.assertEqual(expected_masks, combined._masks)

    def test_successive_merges(self):
        g1, g2, h1, h2 = Mock(), Mock(), Mock(), Mock()
        g1.axes, g2.axes = ["g1x"], ["g2x", "g2y"]
        g1.positions = {"g1x":np.array([0, 1, 2, 3, 4])}
        g2.positions = {
            "g2x":np.array([10, 11, 12, 13, 14, 15, 16]),
            "g2y":np.array([-10, -11, -12, -13, -14, -15, -16])}
        h1.axes, h2.axes = ["h1x", "h1y"], ["h2x"]
        h1.positions = {
            "h1x":np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
            "h1y":np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])}
        h2.positions = {"h2x":np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 9])}
        g1.size, g2.size = 5, 7
        h1.size, h2.size = 11, 13
        g2mask = Mock()
        h1mask = Mock()
        dg1, dg2 = Dimension(g1), Dimension(g2)
        dh1, dh2 = Dimension(h1), Dimension(h2)
        dg2._masks = [{"repeat":1, "tile":1, "mask":g2mask}]
        dh1._masks = [{"repeat":1, "tile":1, "mask":h1mask}]

        outer = Dimension.merge_dimensions(dg1, dg2)
        inner = Dimension.merge_dimensions(dh1, dh2)
        self.assertEqual(5 * 7, outer._max_length)
        self.assertEqual(11 * 13, inner._max_length)
        self.assertEqual([{"repeat":1, "tile":5, "mask":g2mask}], outer._masks)
        self.assertEqual([{"repeat":13, "tile":1, "mask":h1mask}], inner._masks)
        self.assertEqual([4, 16, -10], outer.upper)
        self.assertEqual([0, 10, -16], outer.lower)
        self.assertEqual([11, 21, 9], inner.upper)
        self.assertEqual([1, 1, 0], inner.lower)
        combined = Dimension.merge_dimensions(outer, inner)

        expected_masks = [
            {"repeat":11*13, "tile":5, "mask":g2mask},
            {"repeat":13, "tile":5*7, "mask":h1mask}]
        self.assertEqual(expected_masks, combined._masks)
        self.assertEqual(5 * 7 * 11 * 13, combined._max_length)
        self.assertEqual(["g1x", "g2x", "g2y", "h1x", "h1y", "h2x"], combined.axes)
        self.assertEqual([4, 16, -10, 11, 21, 9], combined.upper)
        self.assertEqual([0, 10, -16, 1, 1, 0], combined.lower)

    def test_prepare(self):
        d = Dimension(Mock(axes=["x", "y"], positions={"x":np.array([0]), "y":np.array([0])}, size=30))
        m1 = np.array([0, 1, 0, 1, 1, 0], dtype=np.int8)
        m2 = np.array([1, 1, 0, 0, 1], dtype=np.int8)
        d._masks = [
            {"repeat":2, "tile":2.5, "mask":m1},
            {"repeat":2, "tile":3, "mask":m2}]
        e1 = np.array([0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0], dtype=np.int8)
        e1 = np.append(np.tile(e1, 2), e1[:len(e1)//2])
        e2 = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1], dtype=np.int8)
        e2 = np.tile(e2, 3)
        expected = e1 & e2
        d.prepare()
        self.assertEqual(expected.tolist(), d.mask.tolist())

    def test_apply_excluder_over_single_gen(self):
        x_pos = np.array([1, 2, 3, 4, 5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        g = Mock(axes=["x", "y"], positions={"x":x_pos, "y":y_pos})
        g.alternate = False
        mask = np.array([1, 1, 0, 1, 0, 0], dtype=np.int8)
        e = Mock(axes=["x", "y"], create_mask=Mock(return_value=mask))
        d = Dimension(g)
        d.apply_excluder(e)
        d._masks[0]["mask"] = d._masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":1, "mask":mask.tolist()}], d._masks)
        self.assertTrue((x_pos == e.create_mask.call_args[0][0]).all())
        self.assertTrue((y_pos == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_over_multiple_gens(self):
        gx_pos = np.array([1, 2, 3, 4, 5])
        gy_pos = np.zeros(5)
        hx_pos = np.zeros(5)
        hy_pos = np.array([-1, -2, -3])
        mask = np.full(15, 1, dtype=np.int8)
        e = Mock(axes=["gx", "hy"], create_mask=Mock(return_value=mask))
        g = Mock(axes=["gx", "gy"], positions={"gx":gx_pos, "gy":gy_pos}, size=len(gx_pos), alternate=False)
        h = Mock(axes=["hx", "hy"], positions={"hx":hx_pos, "hy":hy_pos}, size=len(hy_pos), alternate=False)
        d = Dimension(g)
        d.generators = [g, h]
        d.size = g.size * h.size
        d.apply_excluder(e)
        d._masks[0]["mask"] = d._masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":1, "mask":mask.tolist()}], d._masks)
        self.assertTrue((np.repeat(np.array([1, 2, 3, 4, 5]), 3) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.tile(np.array([-1, -2, -3]), 5) == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_over_single_alternating(self):
        x_pos = np.array([1, 2, 3, 4, 5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        g = Mock(axes=["x", "y"], positions={"x":x_pos, "y":y_pos})
        g.alternate = True
        mask = np.array([1, 1, 0, 1, 0, 0], dtype=np.int8)
        e = Mock(axes=["x", "y"], create_mask=Mock(return_value=mask))
        d = Dimension(g)
        d.apply_excluder(e)
        d._masks[0]["mask"] = d._masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":0.5, "mask":mask.tolist()}], d._masks)
        self.assertTrue((np.append(x_pos, x_pos[::-1]) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.append(y_pos, y_pos[::-1]) == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_with_scaling(self):
        g1_pos = np.array([1, 2, 3])
        g2_pos = np.array([-1, -2])
        mask_func = lambda px, py: np.full(len(px), 1, dtype=np.int8)
        g1 = Mock(axes=["g1"], positions={"g1":g1_pos}, size=len(g1_pos))
        g2 = Mock(axes=["g2"], positions={"g2":g2_pos}, size=len(g2_pos))
        e = Mock(axes=["g1", "g2"], create_mask=Mock(side_effect=mask_func))
        d = Dimension(g1)
        d.alternate = True
        d.generators = [Mock(size=5, axes=[]), g1, g2, Mock(size=7, axes=[])]
        d.size = 5 * len(g1_pos) * len(g2_pos) * 7
        d.apply_excluder(e)
        d._masks[0]["mask"] = d._masks[0]["mask"].tolist()
        expected_mask = [1] * 12
        self.assertEqual([{"repeat":7, "tile":2.5, "mask":expected_mask}], d._masks)
        self.assertTrue((np.repeat(np.append(g1_pos, g1_pos[::-1]), 2) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.tile(np.append(g2_pos, g2_pos[::-1]), 3) == e.create_mask.call_args[0][1]).all())

    def test_get_positions_single_gen(self):
        gx_pos = np.tile(np.array([0, 1, 2, 3]), 4)
        gy_pos = np.repeat(np.array([0, 1, 2, 3]), 4)
        mask_func = lambda px, py: (px-1)**2 + (py-2)**2 <= 1
        g = Mock(axes=["gx", "gy"], positions={"gx":gx_pos, "gy":gy_pos}, size=16, alternate=False)
        e = Mock(axes=["gx", "gy"], create_mask=Mock(side_effect=mask_func))
        d = Dimension(g)
        d.apply_excluder(e)
        d.prepare()
        self.assertEqual([1, 0, 1, 2, 1], d.get_positions("gx").tolist())
        self.assertEqual([1, 2, 2, 2, 3], d.get_positions("gy").tolist())

    def test_get_positions_after_merge(self):
        gx_pos = np.array([0, 1, 2, 3])
        gy_pos = np.array([0, 1, 2, 3])
        mask_func = lambda px, py: (px-1)**2 + (py-2)**2 <= 1
        gx = Mock(axes=["gx"], positions={"gx":gx_pos}, size=4, alternate=False)
        gy = Mock(axes=["gy"], positions={"gy":gy_pos}, size=4, alternate=False)
        e = Mock(axes=["gx", "gy"], create_mask=Mock(side_effect=mask_func))
        dx = Dimension(gx)
        dy = Dimension(gy)
        d = Dimension.merge_dimensions(dy, dx)
        d.apply_excluder(e)
        d.prepare()
        self.assertEqual([1, 0, 1, 2, 1], d.get_positions("gx").tolist())
        self.assertEqual([1, 2, 2, 2, 3], d.get_positions("gy").tolist())

    def test_get_positions_with_alternating(self):
        gx_pos = np.array([0, 1, 2, 3])
        gy_pos = np.array([0, 1, 2, 3])
        gz_pos = np.array([0, 1, 2, 3])
        mask_xy_func = lambda px, py: (px-1)**2 + (py-2)**2 <= 2
        mask_yz_func = lambda py, pz: (py-2)**2 + (pz-1)**2 <= 1
        exy = Mock(axes=["gx", "gy"], create_mask=Mock(side_effect=mask_xy_func))
        eyz = Mock(axes=["gy", "gz"], create_mask=Mock(side_effect=mask_yz_func))
        gx = Mock(axes=["gx"], positions={"gx":gx_pos}, size=4, alternate=True)
        gy = Mock(axes=["gy"], positions={"gy":gy_pos}, size=4, alternate=True)
        gz = Mock(axes=["gz"], positions={"gz":gz_pos}, size=4, alternate=True)
        dx = Dimension(gx)
        dy = Dimension(gy)
        dz = Dimension(gz)
        dz.prepare()
        self.assertEqual([0, 1, 2, 3], dz.get_positions("gz").tolist())
        dyx = Dimension.merge_dimensions(dy, dx)
        dyx.apply_excluder(exy)
        dyx.prepare()
        self.assertEqual([2, 1, 0, 0, 1, 2, 2, 1, 0], dyx.get_positions("gx").tolist())
        self.assertEqual([1, 1, 1, 2, 2, 2, 3, 3, 3], dyx.get_positions("gy").tolist())
        d = Dimension.merge_dimensions(dz, dyx)
        d.apply_excluder(eyz)
        d.prepare()
        self.assertEqual(15, d.size)
        self.assertEqual(
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
            d.get_positions("gz").tolist())
        self.assertEqual(
            [2, 2, 2, 3, 3, 3, 2, 2, 2, 1, 1, 1, 2, 2, 2],
            d.get_positions("gy").tolist())
        self.assertEqual(
            [0, 1, 2, 0, 1, 2, 2, 1, 0, 0, 1, 2, 0, 1, 2],
            d.get_positions("gx").tolist())


if __name__ == "__main__":
    unittest.main(verbosity=2)
