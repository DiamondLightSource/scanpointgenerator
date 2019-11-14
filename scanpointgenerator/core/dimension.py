###
# Copyright (c) 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import itertools

from scanpointgenerator.compat import np


class Dimension(object):
    """
    An unrolled set of generators joined by excluders.
    Represents a single dimension within a scan.
    """

    def __init__(self, generators, excluders=None):
        self.generators = list(generators)
        self.excluders = list(excluders) if excluders is not None else []
        self.axes = list(axis for g in self.generators for axis in g.axes)
        """list(str): Unrolled axes within the dimension"""
        self.size = None
        """int: Size of the dimension"""
        self.upper = [g.positions[a].max((0,)) for g in self.generators for a in g.axes]
        """list(float): Upper bound for the dimension"""
        self.lower = [g.positions[a].min((0,)) for g in self.generators for a in g.axes]
        """list(float): Lower bound for the dimension"""
        self.alternate = self.generators[0].alternate
        self._prepared = False
        self.indices = []

        # validate alternating constraints
        # we currently do not allow a non-alternating generator inside an
        # alternating one due to potentially "surprising" behaviour of the
        # non-alternating generator (the dimension itself will be alternating)
        started_alternating = False
        for g in self.generators:
            if started_alternating and not g.alternate:
                raise ValueError(
                        "Cannot nest non-alternating generators in "
                        "alternating generators within a Dimension "
                        "due to inconsistent output paths")
            started_alternating = started_alternating or g.alternate


    def apply_excluder(self, excluder):
        """Add an excluder to the current Dimension"""
        if self._prepared:
            raise ValueError("Dimension already prepared")
        if not set(excluder.axes) <= set(self.axes):
            raise ValueError("Excluder axes '%s' do not apply to Dimension axes '%s'" \
                    % (excluder.axes, self.axes))
        self.excluders.append(excluder)


    def get_positions(self, axis):
        """
        Retrieve the positions for a given axis within the dimension.

        Args:
            axis (str): axis to get positions for
        Returns:
            Positions (np.array): Array of positions
        """
        # check that this dimension is prepared
        if not self._prepared:
            raise ValueError("Must call prepare first")
        return self.positions[axis]


    def get_mesh_map(self, axis):
        """
        Retrieve the mesh map (indices) for a given axis within the dimension.

        Args:
            axis (str): axis to get positions for
        Returns:
            Positions (np.array): Array of mesh indices
        """
        # the points for this axis must be scaled and then indexed
        if not self._prepared:
            raise ValueError("Must call prepare first")
        # scale up points for axis
        gen = [g for g in self.generators if axis in g.axes][0]
        points = gen.positions[axis]
        # just get index of points instead of actual point value
        points = np.arange(len(points))

        if gen.alternate:
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


    def get_point(self, idx):
        if not self._prepared:
            raise ValueError("Must call prepare first")
        axis_points = {axis:self.positions[axis][idx] for axis in self.positions}
        return axis_points


    def get_bounds(self, idx, reverse=False):
        if not self._prepared:
            raise ValueError("Must call prepare first")
        if not reverse:
            axis_upper, axis_lower = self.upper_bounds, self.lower_bounds
        else:
            axis_upper, axis_lower = self.lower_bounds, self.upper_bounds
        lower = {axis:axis_lower[axis][idx] for axis in axis_lower}
        upper = {axis:axis_upper[axis][idx] for axis in axis_upper}
        return lower, upper


    def prepare(self):
        """
        Prepare data structures required to determine size and
        filtered positions of the dimension.
        Must be called before get_positions or get_mesh_map are called.
        """
        axis_positions = {}
        axis_bounds_lower = {}
        axis_bounds_upper = {}
        masks = []
        # scale up all position arrays
        # inner generators are tiled by the size of out generators
        # outer generators have positions repeated by the size of inner generators
        repeats, tilings, dim_size = 1, 1, 1
        for g in self.generators:
            repeats *= g.size
            dim_size *= g.size

        for gen in self.generators:
            repeats /= gen.size
            for axis in gen.axes:
                positions = gen.positions[axis]
                if gen.alternate:
                    positions = np.append(positions, positions[::-1])
                    positions = np.repeat(positions, repeats)
                    p = np.tile(positions, (tilings // 2))
                    if tilings % 2 != 0:
                        positions = np.append(p, positions[:int(len(positions)//2)])
                    else:
                        positions = p
                else:
                    positions = np.repeat(positions, repeats)
                    positions = np.tile(positions, tilings)
                axis_positions[axis] = positions
            tilings *= gen.size

        # produce excluder masks
        for excl in self.excluders:
            arrays = [axis_positions[axis] for axis in excl.axes]
            excluder_mask = excl.create_mask(*arrays)
            masks.append(excluder_mask)

        # AND all masks together (empty mask is all values selected)
        mask = masks[0] if len(masks) else np.full(dim_size, True, dtype=np.int8)
        for m in masks[1:]:
            mask &= m

        gen = self.generators[-1]
        if getattr(gen, "bounds", None):
            tilings = np.prod(np.array([g.size for g in self.generators[:-1]]))
            if gen.alternate:
                tilings /= 2.
            for axis in gen.axes:
                upper_base = gen.bounds[axis][1:]
                lower_base = gen.bounds[axis][:-1]
                upper, lower = upper_base, lower_base
                if gen.alternate:
                    upper = np.append(upper_base, lower_base[::-1])
                    lower = np.append(lower_base, upper_base[::-1])
                upper = np.tile(upper, int(tilings))
                lower = np.tile(lower, int(tilings))
                if tilings % 1 != 0:
                    upper = np.append(upper, upper_base)
                    lower = np.append(lower, lower_base)
                axis_bounds_upper[axis] = upper
                axis_bounds_lower[axis] = lower

        self.mask = mask
        self.indices = self.mask.nonzero()[0]
        self.size = len(self.indices)
        self.positions = {axis:axis_positions[axis][self.indices] for axis in axis_positions}
        self.upper_bounds = {axis:self.positions[axis] for axis in self.positions}
        self.lower_bounds = {axis:self.positions[axis] for axis in self.positions}
        for axis in axis_bounds_lower:
            self.upper_bounds[axis] = axis_bounds_upper[axis][self.indices]
            self.lower_bounds[axis] = axis_bounds_lower[axis][self.indices]
        self._prepared = True


    @staticmethod
    def merge_dimensions(dimensions):
        generators = itertools.chain.from_iterable(d.generators for d in dimensions)
        excluders = itertools.chain.from_iterable(d.excluders for d in dimensions)
        return Dimension(generators, excluders)
