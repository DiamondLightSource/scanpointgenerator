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
        # find generators referenced by excluder
        matched_gens = [g for g in self.generators if len(set(g.axes) & set(excluder.axes)) != 0]
        if len(matched_gens) == 0:
            raise ValueError("Excluder references axes not present in dimension : %s" % str(excluder.axes))
        g_start = self.generators.index(matched_gens[0])
        g_end = self.generators.index(matched_gens[-1])
        point_arrays = {axis:[g for g in matched_gens if axis in g.axes][0].positions[axis] for axis in excluder.axes}

        if self.alternate:
            for axis in point_arrays.keys():
                arr = point_arrays[axis]
                point_arrays[axis] = np.append(arr, arr[::-1])

        # scale up all point arrays using generators within the range
        # inner generators are tiled by the size of outer generators
        # outer generators have points repeated by the size of inner ones
        axes_tiling = {axis:1 for axis in excluder.axes}
        axes_repeats = {axis:1 for axis in excluder.axes}
        axes_seen = []
        axes_to_see = [axis for axis in excluder.axes]
        for g in self.generators[g_start:g_end+1]:
            found_axes = [axis for axis in g.axes if axis in excluder.axes]
            axes_to_see = [axis for axis in axes_to_see if axis not in found_axes]
            for axis in axes_to_see:
                axes_tiling[axis] *= g.size
            for axis in axes_seen:
                axes_repeats[axis] *= g.size
            axes_seen.extend(found_axes)
        for axis in point_arrays.keys():
            arr = point_arrays[axis]
            point_arrays[axis] = np.tile(np.repeat(arr, axes_repeats[axis]), axes_tiling[axis])

        arrays = [point_arrays[axis] for axis in excluder.axes]
        excluder_mask = excluder.create_mask(*arrays)

        # record the tiling/repeat information for generators outside the axis range
        tile = 0.5 if self.alternate else 1
        repeat = 1
        for g in self.generators[0:g_start]:
            tile *= g.size
        for g in self.generators[g_end+1:]:
            repeat *= g.size

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
    def merge_dimensions(dimensions):
        """Merge multiple dimensions into one, scaling structures as required

        Args:
            dimensions (list): dimensions to merge (outermost first)
        Returns:
            Dimension: squashed dimension
        """
        final_dim = Dimension(dimensions[0].generators[0])
        final_dim.generators = []
        final_dim.lower = []
        final_dim.upper = []
        final_dim.axes = []
        final_dim._max_length = 1
        # masks in the inner generator are tiled by the size of
        # outer generators and outer generators have their elements
        # repeated by the size of inner generators
        for dim in dimensions:
            inner_masks = [m.copy() for m in dim._masks] # copy masks to preserve input strucutres
            for m in final_dim._masks:
                m["repeat"] *= dim._max_length
            for m in inner_masks:
                m["tile"] *= final_dim._max_length
            final_dim._masks += inner_masks
            final_dim.axes += dim.axes
            final_dim.generators += dim.generators
            final_dim.upper += dim.upper
            final_dim.lower += dim.lower
            final_dim._max_length *= dim._max_length
            final_dim.alternate = final_dim.alternate or dim.alternate
        return final_dim
