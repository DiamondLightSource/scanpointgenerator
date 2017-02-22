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
        d = Dimension(g)
        self.assertEqual([g], d.generators)
        self.assertEqual(["x", "y"], d.axes)
        self.assertEqual([], d.masks)
        self.assertEqual(g.alternate_direction, d.alternate)
        self.assertEqual(g.size, d.size)

    def test_merge_dimensions(self):
        g, h = Mock(), Mock()
        g.axes, h.axes = ["gx", "gy"], ["hx", "hy"]
        g.size, h.size = 16, 64
        outer, inner = Dimension(g), Dimension(h)
        om1, om2 = Mock(), Mock()
        im1, im2 = Mock(), Mock()
        outer.masks = [{"repeat":2, "tile":3, "mask":om1},
            {"repeat":5, "tile":7, "mask":om2}]
        inner.masks = [{"repeat":11, "tile":13, "mask":im1},
            {"repeat":17, "tile":19, "mask":im2}]
        combined = Dimension.merge_dimensions(outer, inner)

        self.assertEqual(g.size * h.size, combined.size)
        self.assertEqual(outer.alternate or inner.alternate, combined.alternate)
        self.assertEqual(["gx", "gy", "hx", "hy"], combined.axes)
        expected_masks = [
            {"repeat":128, "tile":3, "mask":om1},
            {"repeat":320, "tile":7, "mask":om2},
            {"repeat":11, "tile":13*16, "mask":im1},
            {"repeat":17, "tile":19*16, "mask":im2}]
        self.assertEqual(expected_masks, combined.masks)

    def test_successive_merges(self):
        g1, g2, h1, h2 = Mock(), Mock(), Mock(), Mock()
        g1.axes, g2.axes = ["g1x"], ["g2x", "g2y"]
        h1.axes, h2.axes = ["h1x", "h1y"], ["h2x"]
        g1.size, g2.size = 5, 7
        h1.size, h2.size = 11, 13
        g2mask = Mock()
        h1mask = Mock()
        dg1, dg2 = Dimension(g1), Dimension(g2)
        dh1, dh2 = Dimension(h1), Dimension(h2)
        dg2.masks = [{"repeat":1, "tile":1, "mask":g2mask}]
        dh1.masks = [{"repeat":1, "tile":1, "mask":h1mask}]

        outer = Dimension.merge_dimensions(dg1, dg2)
        inner = Dimension.merge_dimensions(dh1, dh2)
        self.assertEqual(5 * 7, outer.size)
        self.assertEqual(11 * 13, inner.size)
        self.assertEqual([{"repeat":1, "tile":5, "mask":g2mask}], outer.masks)
        self.assertEqual([{"repeat":13, "tile":1, "mask":h1mask}], inner.masks)
        combined = Dimension.merge_dimensions(outer, inner)

        expected_masks = [
            {"repeat":11*13, "tile":5, "mask":g2mask},
            {"repeat":13, "tile":5*7, "mask":h1mask}]
        self.assertEqual(expected_masks, combined.masks)
        self.assertEqual(5 * 7 * 11 * 13, combined.size)
        self.assertEqual(["g1x", "g2x", "g2y", "h1x", "h1y", "h2x"], combined.axes)

    def test_create_dimension_mask(self):
        d = Dimension(Mock(axes=["x", "y"]))
        d.size = 30
        m1 = np.array([0, 1, 0, 1, 1, 0], dtype=np.int8)
        m2 = np.array([1, 1, 0, 0, 1], dtype=np.int8)
        d.masks = [
            {"repeat":2, "tile":2.5, "mask":m1},
            {"repeat":2, "tile":3, "mask":m2}]
        e1 = np.array([0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0], dtype=np.int8)
        e1 = np.append(np.tile(e1, 2), e1[:len(e1)//2])
        e2 = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1], dtype=np.int8)
        e2 = np.tile(e2, 3)
        expected = e1 & e2
        mask = d.create_dimension_mask()
        self.assertEqual(expected.tolist(), mask.tolist())

    def test_apply_excluder_over_single_gen(self):
        x_pos = np.array([1, 2, 3, 4, 5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        g = Mock(axes=["x", "y"], positions={"x":x_pos, "y":y_pos})
        g.alternate_direction = False
        mask = np.array([1, 1, 0, 1, 0, 0], dtype=np.int8)
        e = Mock(scannables=["x", "y"], create_mask=Mock(return_value=mask))
        d = Dimension(g)
        d.apply_excluder(e)
        d.masks[0]["mask"] = d.masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":1, "mask":mask.tolist()}], d.masks)
        self.assertTrue((x_pos == e.create_mask.call_args[0][0]).all())
        self.assertTrue((y_pos == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_over_multiple_gens(self):
        gx_pos = np.array([1, 2, 3, 4, 5])
        hy_pos = np.array([-1, -2, -3])
        mask = np.full(15, 1, dtype=np.int8)
        e = Mock(scannables=["gx", "hy"], create_mask=Mock(return_value=mask))
        g = Mock(axes=["gx", "gy"], positions={"gx":gx_pos}, size=len(gx_pos), alternate_direction=False)
        h = Mock(axes=["hx", "hy"], positions={"hy":hy_pos}, size=len(hy_pos), alternate_direction=False)
        d = Dimension(g)
        d.generators = [g, h]
        d.size = g.size * h.size
        d.apply_excluder(e)
        d.masks[0]["mask"] = d.masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":1, "mask":mask.tolist()}], d.masks)
        self.assertTrue((np.repeat([1, 2, 3, 4, 5], 3) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.tile([-1, -2, -3], 5) == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_over_single_alternating(self):
        x_pos = np.array([1, 2, 3, 4, 5])
        y_pos = np.array([10, 11, 12, 13, 14, 15])
        g = Mock(axes=["x", "y"], positions={"x":x_pos, "y":y_pos})
        g.alternate_direction = True
        mask = np.array([1, 1, 0, 1, 0, 0], dtype=np.int8)
        e = Mock(scannables=["x", "y"], create_mask=Mock(return_value=mask))
        d = Dimension(g)
        d.apply_excluder(e)
        d.masks[0]["mask"] = d.masks[0]["mask"].tolist()
        self.assertEqual([{"repeat":1, "tile":0.5, "mask":mask.tolist()}], d.masks)
        self.assertTrue((np.append(x_pos, x_pos[::-1]) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.append(y_pos, y_pos[::-1]) == e.create_mask.call_args[0][1]).all())

    def test_apply_excluders_with_scaling(self):
        g1_pos = np.array([1, 2, 3])
        g2_pos = np.array([-1, -2])
        mask_func = lambda px, py: np.full(len(px), 1, dtype=np.int8)
        g1 = Mock(axes=["g1"], positions={"g1":g1_pos}, size=len(g1_pos))
        g2 = Mock(axes=["g2"], positions={"g2":g2_pos}, size=len(g2_pos))
        e = Mock(scannables=["g1", "g2"], create_mask=Mock(side_effect=mask_func))
        d = Dimension(g1)
        d.alternate = True
        d.generators = [Mock(size=5, axes=[]), g1, g2, Mock(size=7, axes=[])]
        d.size = 5 * len(g1_pos) * len(g2_pos) * 7
        d.apply_excluder(e)
        d.masks[0]["mask"] = d.masks[0]["mask"].tolist()
        expected_mask = [1] * 12
        self.assertEqual([{"repeat":7, "tile":2.5, "mask":expected_mask}], d.masks)
        self.assertTrue((np.repeat(np.append(g1_pos, g1_pos[::-1]), 2) == e.create_mask.call_args[0][0]).all())
        self.assertTrue((np.tile(np.append(g2_pos, g2_pos[::-1]), 3) == e.create_mask.call_args[0][1]).all())

if __name__ == "__main__":
    unittest.main(verbosity=2)
