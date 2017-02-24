from scanpointgenerator.compat import np

class Dimension(object):
    """A collapsed set of generators joined by excluders"""
    def __init__(self, generator):
        self.axes = list(generator.axes)
        self.generators = [generator]
        self.size = generator.size
        self.alternate = generator.alternate
        self._masks = []

    def apply_excluder(self, excluder):
        """Apply an excluder with axes matching some axes in the dimension to
        produce an internal mask"""
        axis_inner = excluder.scannables[0]
        axis_outer = excluder.scannables[1]
        gen_inner = [g for g in self.generators if axis_inner in g.axes][0]
        gen_outer = [g for g in self.generators if axis_outer in g.axes][0]
        points_x = gen_inner.positions[axis_inner]
        points_y = gen_outer.positions[axis_outer]
        if self.generators.index(gen_inner) > self.generators.index(gen_outer):
            gen_inner, gen_outer = gen_outer, gen_inner
            axis_inner, axis_outer = axis_outer, axis_inner
            points_x, points_y = points_y, points_x

        if gen_inner is gen_outer and self.alternate:
            points_x = np.append(points_x, points_x[::-1])
            points_y = np.append(points_y, points_y[::-1])
        elif self.alternate:
            points_x = np.append(points_x, points_x[::-1])
            points_x = np.repeat(points_x, gen_outer.size)
            points_y = np.append(points_y, points_y[::-1])
            points_y = np.tile(points_y, gen_inner.size)
        elif gen_inner is not gen_outer:
            points_x = np.repeat(points_x, gen_outer.size)
            points_y = np.tile(points_y, gen_inner.size)
        else:
            # copy the point arrays so the excluders can perform
            # array operations in place (advantageous in the other cases)
            points_x = np.copy(points_x)
            points_y = np.copy(points_y)

        if axis_inner == excluder.scannables[0]:
            mask = excluder.create_mask(points_x, points_y)
        else:
            mask = excluder.create_mask(points_y, points_x)
        tile = 0.5 if self.alternate else 1
        repeat = 1
        found_axis = False
        for g in self.generators:
            if axis_inner in g.axes or axis_outer in g.axes:
                found_axis = True
            else:
                if found_axis:
                    repeat *= g.size
                else:
                    tile *= g.size

        m = {"repeat":repeat, "tile":tile, "mask":mask}
        self._masks.append(m)

    def create_dimension_mask(self):
        """
        Create and return a mask for every point in the dimension

        e.g. (with [y1, y2, y3] and [x1, x2, x3] both alternating)
        y:    y1, y1, y1, y2, y2, y2, y3, y3, y3
        x:    x1, x2, x3, x3, x2, x1, x1, x2, x3
        mask: m1, m2, m3, m4, m5, m6, m7, m8, m9

        Returns:
            np.array(int8): One dimensional mask array
        """
        mask = np.full(self.size, True, dtype=np.int8)
        for m in self._masks:
            assert len(m["mask"]) * m["repeat"] * m["tile"] == len(mask), \
                "Mask lengths are not consistent"
            expanded = np.repeat(m["mask"], m["repeat"])
            if m["tile"] % 1 != 0:
                ex = np.tile(expanded, int(m["tile"]))
                expanded = np.append(ex, expanded[:int(len(expanded)//2)])
            else:
                expanded = np.tile(expanded, int(m["tile"]))
            mask &= expanded
        return mask

    @staticmethod
    def merge_dimensions(outer, inner):
        """Collapse two dimensions into one, appropriate scaling structures"""
        dim = Dimension(outer.generators[0])
        # masks in the inner generator are tiled by the size of
        # outer generators and outer generators have their elements
        # repeated by the size of inner generators
        inner_masks = [m.copy() for m in inner._masks]
        outer_masks = [m.copy() for m in outer._masks]
        scale = inner.size
        for m in outer_masks:
            m["repeat"] *= scale
        scale = outer.size
        for m in inner_masks:
            m["tile"] *= scale
        dim._masks = outer_masks + inner_masks
        dim.axes = outer.axes + inner.axes
        dim.generators = outer.generators + inner.generators
        dim.alternate = outer.alternate or inner.alternate
        dim.size = outer.size * inner.size
        return dim
