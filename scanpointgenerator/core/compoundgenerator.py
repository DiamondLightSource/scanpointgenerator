###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import logging

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core.dimension import Dimension
from scanpointgenerator.core.generator import Generator
from scanpointgenerator.core.point import Point
from scanpointgenerator.core.excluder import Excluder
from scanpointgenerator.excluders.roiexcluder import ROIExcluder
from scanpointgenerator.core.mutator import Mutator
from scanpointgenerator.rois import RectangularROI
from scanpointgenerator.generators import LineGenerator, StaticPointGenerator


class CompoundGenerator(object):
    """Nest N generators, apply exclusion regions to relevant generator pairs
    and apply any mutators before yielding points"""

    typeid = "scanpointgenerator:generator/CompoundGenerator:1.0"

    def __init__(self, generators, excluders, mutators, duration=-1, continuous=True):
        """
        Args:
            generators(list(Generator)): List of Generators to nest
            excluders(list(Excluder)): List of Excluders to filter points by
            mutators(list(Mutator)): List of Mutators to apply to each point
            duration(double): Point durations in seconds (-1 for variable)
            continuous(boolean): Make points continuous (set upper/lower bounds)
        """

        self.size = 0
        """int: Final number of points to be generated -
        valid only after calling prepare"""
        self.shape = None
        """tuple(int): Final shape of the scan -
        valid only after calling prepare"""
        self.dimensions = []
        """list(Dimension): Dimension instances -
        valid only after calling prepare"""

        self.excluders = excluders
        self.mutators = mutators
        self.axes = []
        self.units = {}
        self.duration = duration
        self._dim_meta = {}
        self._prepared = False
        self.continuous = continuous
        for generator in generators:
            logging.debug("Generator passed to Compound init")
            logging.debug(generator.to_dict())
            if isinstance(generator, self.__class__):
                raise TypeError("CompoundGenerators cannot be nested, nest"
                                "its constituent parts instead")
            self.axes += generator.axes
            self.units.update(generator.units)
        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated")

        self.generators = generators
        self._generator_dim_scaling = {}

    def prepare(self):
        """
        Prepare data structures required for point generation and
        initialize size, shape, and dimensions attributes.
        Must be called before get_point or iterator are called.
        """
        if self._prepared:
            return
        self.dimensions = []
        self._dim_meta = {}
        self._generator_dim_scaling = {}

        # we're going to mutate these structures
        excluders = list(self.excluders)
        generators = list(self.generators)

        # special case if we have rectangular regions on line generators
        # we should restrict the resulting grid rather than merge dimensions
        # this changes the alternating case a little (without doing this, we
        # may have started in reverse direction)
        for excluder_ in [e for e in excluders if isinstance(e, ROIExcluder)]:
            if len(excluder_.rois) == 1 \
                    and isinstance(excluder_.rois[0], RectangularROI) \
                    and excluder_.rois[0].angle == 0:
                rect = excluder_.rois[0]
                axis_1, axis_2 = excluder_.axes[0], excluder_.axes[1]
                gen_1 = [g for g in generators if axis_1 in g.axes][0]
                gen_2 = [g for g in generators if axis_2 in g.axes][0]
                if gen_1 is gen_2:
                    continue
                if isinstance(gen_1, LineGenerator) \
                        and isinstance(gen_2, LineGenerator):
                    gen_1.prepare_positions()
                    gen_2.prepare_positions()
                    # Filter by axis 1
                    valid = np.full(gen_1.size, True, dtype=np.int8)
                    valid &= \
                        gen_1.positions[axis_1] <= rect.width + rect.start[0]
                    valid &= \
                        gen_1.positions[axis_1] >= rect.start[0]
                    points_1 = gen_1.positions[axis_1][valid.astype(np.bool)]
                    # Filter by axis 2
                    valid = np.full(gen_2.size, True, dtype=np.int8)
                    valid &= \
                        gen_2.positions[axis_2] <= rect.height + rect.start[1]
                    valid &= gen_2.positions[axis_2] >= rect.start[1]
                    points_2 = gen_2.positions[axis_2][valid.astype(np.bool)]
                    # Recreate generators to replace larger generators + ROI
                    new_gen1 = LineGenerator(
                        gen_1.axes, gen_1.units, points_1[0], points_1[-1],
                        len(points_1), gen_1.alternate)
                    new_gen2 = LineGenerator(
                        gen_2.axes, gen_2.units, points_2[0], points_2[-1],
                        len(points_2), gen_2.alternate)
                    generators[generators.index(gen_1)] = new_gen1
                    generators[generators.index(gen_2)] = new_gen2
                    # Remove Excluder as it is now empty
                    excluders.remove(excluder_)

        for generator in generators:
            generator.prepare_positions()
            self.dimensions.append(Dimension(generator))
        # only the inner-most generator needs to have bounds calculated
        if self.continuous:
            generators[-1].prepare_bounds()

        for excluder in excluders:
            matched_dims = [d for d in self.dimensions if len(set(d.axes) & set(excluder.axes)) != 0]
            if len(matched_dims) == 0:
                raise ValueError(
                        "Excluder references axes that have not been provided by generators: %s" % str(excluder.axes))
            d_start = self.dimensions.index(matched_dims[0])
            d_end = self.dimensions.index(matched_dims[-1])
            if d_start != d_end:
                # merge all excluders between d_start and d_end (inclusive)
                alternate = self.dimensions[d_end].alternate
                # verify consistent alternate settings (ignoring outermost dimesion where it doesn't matter)
                for d in self.dimensions[max(1, d_start):d_end]:
                    # filter out dimensions consisting of a single StaticPointGenerator, since alternation means nothing
                    if len(d.generators) == 1 and isinstance(d.generators[0], StaticPointGenerator):
                        continue
                    if alternate != d.alternate:
                        raise ValueError("Nested generators connected by regions must have the same alternate setting")
                merged_dim = Dimension.merge_dimensions(self.dimensions[d_start:d_end+1])
                self.dimensions = self.dimensions[:d_start] + [merged_dim] + self.dimensions[d_end+1:]
                dim = merged_dim
            else:
                dim = self.dimensions[d_start]
            dim.apply_excluder(excluder)

        self.size = 1
        for dim in self.dimensions:
            self._dim_meta[dim] = {}
            dim.prepare()
            if dim.size == 0:
                raise ValueError("Regions would exclude entire scan")
            self.size *= dim.size

        self.shape = tuple(dim.size for dim in self.dimensions)
        repeat = self.size
        tile = 1
        for dim in self.dimensions:
            repeat /= dim.size
            self._dim_meta[dim]["tile"] = tile
            self._dim_meta[dim]["repeat"] = repeat
            tile *= dim.size

        for dim in self.dimensions:
            tile = 1
            repeat = dim._max_length
            for g in dim.generators:
                repeat /= g.size
                d = {"tile":tile, "repeat":repeat}
                tile *= g.size
                self._generator_dim_scaling[g] = d

        self._prepared = True

    def iterator(self):
        """
        Iterator yielding generator positions at each scan point

        Yields:
            Point: The next point
        """
        if not self._prepared:
            raise ValueError("CompoundGenerator has not been prepared")
        it = (self.get_point(n) for n in range_(self.size))
        for p in it:
            yield p

    def get_point(self, n):
        """
        Retrieve the desired point from the generator

        Args:
            n (int): point to be generated
        Returns:
            Point: The requested point
        """

        if not self._prepared:
            raise ValueError("CompoundGenerator has not been prepared")
        if n >= self.size:
            raise IndexError("Requested point is out of range")
        point = Point()

        # need to know how far along each dimension we are
        # and, in the case of alternating indices, how
        # many times we've run through them
        kc = 0 # the "cumulative" k for each dimension
        for dim in self.dimensions:
            i = int(n // self._dim_meta[dim]["repeat"])
            i %= dim.size
            k = dim.indices[i]
            dim_reverse = False
            if dim.alternate and kc % 2 == 1:
                i = dim.size - i - 1
                dim_reverse = True
            kc *= dim.size
            kc += k
            k = dim.indices[i]
            # need point k along each generator in dimension
            # in alternating case, need to sometimes go backward
            point.indexes.append(i)
            for g in dim.generators:
                j = int(k // self._generator_dim_scaling[g]["repeat"])
                r = int(j // g.size)
                j %= g.size
                j_lower = j
                j_upper = j + 1
                if dim.alternate and g is not dim.generators[0] and r % 2 == 1:
                    # the top level generator's direction is handled by
                    # the fact that the reverse direction was appended
                    j = g.size - j - 1
                    j_lower = j + 1
                    j_upper = j
                elif dim_reverse and g is dim.generators[0]:
                    # top level generator is running in reverse,
                    # so bounds are swapped
                    j_lower, j_upper = j_upper, j_lower
                for axis in g.axes:
                    point.positions[axis] = g.positions[axis][j]
                    # apply "real" bounds to the "innermost" generator only
                    if self.continuous and dim is self.dimensions[-1] and g is dim.generators[-1]:
                        point.lower[axis] = g.bounds[axis][j_lower]
                        point.upper[axis] = g.bounds[axis][j_upper]
                    else:
                        point.lower[axis] = g.positions[axis][j]
                        point.upper[axis] = g.positions[axis][j]
        point.duration = self.duration
        for m in self.mutators:
            point = m.mutate(point, n)
        return point

    def to_dict(self):
        """Convert object attributes into a dictionary"""
        d = {}
        d['typeid'] = self.typeid
        d['generators'] = [g.to_dict() for g in self.generators]
        d['excluders'] = [e.to_dict() for e in self.excluders]
        d['mutators'] = [m.to_dict() for m in self.mutators]
        d['duration'] = float(self.duration)
        d['continuous'] = self.continuous
        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a CompoundGenerator instance from a serialised dictionary

        Args:
            d(dict): Dictionary of attributes
        Returns:
            CompoundGenerator: New CompoundGenerator instance
        """
        generators = [Generator.from_dict(g) for g in d['generators']]
        excluders = [Excluder.from_dict(e) for e in d['excluders']]
        mutators = [Mutator.from_dict(m) for m in d['mutators']]
        duration = d['duration']
        continuous = d['continuous']
        return cls(generators, excluders, mutators, duration, continuous)
