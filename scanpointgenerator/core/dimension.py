###
# Copyright (c) 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from scanpointgenerator.compat import np


class Dimension(object):
    """
    An unrolled set of generators joined by excluders.
    Represents a single dimension within a scan.
    """

    def __init__(self, generator):
        self.axes = list(generator.axes)
        """list(int): Unrolled axes within the dimension"""
        self.size = None
        """int: Size of the dimension"""
        self.upper = [generator.positions[a].max((0,)) for a in generator.axes]
        """list(float): Upper bound for the dimension"""
        self.lower = [generator.positions[a].min((0,)) for a in generator.axes]
        """list(float): Lower bound for the dimension"""
        self.alternate = generator.alternate
        self.generators = [generator]
        self._masks = []
        self._max_length = generator.size
        self._prepared = False
        self.indices = []

    def get_positions(self, axis):
        """
        Retrieve the positions for a given axis within the dimension.

        Args:
            axis (str): axis to get positions for
        Returns:
            Positions (np.array): Array of positions
        """
        # the points for this axis must be scaled and then indexed
        if not self._prepared:
            raise ValueError("Must call prepare first")
        # scale up points for axis
        gen = [g for g in self.generators if axis in g.axes][0]
        points = gen.positions[axis]
        if self.alternate:
            points = np.append(points, points[::-1])
        tile = 0.5 if self.alternate else 1
        repeat = 1
        for g in self.generators[:self.generators.index(gen)]:
            tile *= g.size
        for g in self.generators[self.generators.index(gen) + 1:]:
            repeat *= g.size
        points = np.repeat(points, repeat)
        if tile % 1 != 0:
            p = np.tile(points, int(tile))
            points = np.append(p, points[:int(len(points)//2)])
        else:
            points = np.tile(points, int(tile))
        return points[self.indices]


    def apply_excluder(self, excluder):
        """Apply an excluder with axes matching some axes in the dimension to
        produce an internal mask"""
        if self._prepared:
            raise ValueError("Can not apply excluders after"
                             "prepare has been called")
        axis_inner = excluder.axes[0]
        axis_outer = excluder.axes[1]
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

        if axis_inner == excluder.axes[0]:
            excluder_mask = excluder.create_mask(points_x, points_y)
        else:
            excluder_mask = excluder.create_mask(points_y, points_x)
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

        m = {"repeat":repeat, "tile":tile, "mask":excluder_mask}
        self._masks.append(m)

    def prepare(self):
        """
        Create and return a mask for every point in the dimension

        e.g. (with [y1, y2, y3] and [x1, x2, x3] both alternating)
        y:    y1, y1, y1, y2, y2, y2, y3, y3, y3
        x:    x1, x2, x3, x3, x2, x1, x1, x2, x3
        mask: m1, m2, m3, m4, m5, m6, m7, m8, m9

        Returns:
            np.array(int8): One dimensional mask array
        """
        if self._prepared:
            return
        mask = np.full(self._max_length, True, dtype=np.int8)
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
        # we have to assume the "returned" mask may be edited in place
        # so we have to store a copy
        self.mask = mask
        self.indices = self.mask.nonzero()[0]
        self.size = len(self.indices)
        self._prepared = True

    @staticmethod
    def merge_dimensions(outer, inner):
        """Collapse two dimensions into one, appropriate scaling structures"""
        dim = Dimension(outer.generators[0])
        # masks in the inner generator are tiled by the size of
        # outer generators and outer generators have their elements
        # repeated by the size of inner generators
        inner_masks = [m.copy() for m in inner._masks]
        outer_masks = [m.copy() for m in outer._masks]
        scale = inner._max_length
        for m in outer_masks:
            m["repeat"] *= scale
        scale = outer._max_length
        for m in inner_masks:
            m["tile"] *= scale
        dim._masks = outer_masks + inner_masks
        dim.axes = outer.axes + inner.axes
        dim.generators = outer.generators + inner.generators
        dim.alternate = outer.alternate or inner.alternate
        dim._max_length = outer._max_length * inner._max_length
        dim.upper = outer.upper + inner.upper
        dim.lower = outer.lower + inner.lower
        return dim
