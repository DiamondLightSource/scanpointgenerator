import logging

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core.dimension import Dimension
from scanpointgenerator.core.generator import Generator
from scanpointgenerator.core.point import Point
from scanpointgenerator.core.excluder import Excluder
from scanpointgenerator.core.mutator import Mutator
from scanpointgenerator.rois import RectangularROI
from scanpointgenerator.generators import LineGenerator


class CompoundGenerator(object):
    """Nest N generators, apply exclusion regions to relevant generator pairs
    and apply any mutators before yielding points"""

    typeid = "scanpointgenerator:generator/CompoundGenerator:1.0"

    def __init__(self, generators, excluders, mutators):
        """
        Args:
            generators(list(Generator)): List of Generators to nest
            excluders(list(Excluder)): List of Excluders to filter points by
            mutators(list(Mutator)): List of Mutators to apply to each point
        """

        self.excluders = excluders
        self.mutators = mutators
        self.axes = []
        self.units = {}
        self.dimensions = []
        self.size = 1
        self._dim_meta = {}
        self._prepared = False
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
        Prepare data structures and masks required for point generation.
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
        for rect in [r for r in excluders \
                if isinstance(r.roi, RectangularROI) and r.roi.angle == 0]:
            axis_1, axis_2 = rect.scannables[0], rect.scannables[1]
            gen_1 = [g for g in generators if axis_1 in g.axes][0]
            gen_2 = [g for g in generators if axis_2 in g.axes][0]
            if gen_1 is gen_2:
                continue
            if isinstance(gen_1, LineGenerator) \
                    and isinstance(gen_2, LineGenerator):
                gen_1.prepare_positions()
                gen_2.prepare_positions()
                valid = np.full(gen_1.size, True, dtype=np.int8)
                valid &= gen_1.positions[axis_1] \
                        <= rect.roi.width + rect.roi.start[0]
                valid &= gen_1.positions[axis_1] >= rect.roi.start[0]
                points_1 = gen_1.positions[axis_1][valid.astype(np.bool)]
                valid = np.full(gen_2.size, True, dtype=np.int8)
                valid &= gen_2.positions[axis_2] \
                        <= rect.roi.height + rect.roi.start[1]
                valid &= gen_2.positions[axis_2] >= rect.roi.start[1]
                points_2 = gen_2.positions[axis_2][valid.astype(np.bool)]
                new_gen1 = LineGenerator(
                    gen_1.axes, gen_1.units, points_1[0], points_1[-1],
                    len(points_1), gen_1.alternate)
                new_gen2 = LineGenerator(
                    gen_2.axes, gen_2.units, points_2[0], points_2[-1],
                    len(points_2), gen_2.alternate)
                generators[generators.index(gen_1)] = new_gen1
                generators[generators.index(gen_2)] = new_gen2
                excluders.remove(rect)

        for generator in generators:
            generator.prepare_positions()
            self.dimensions.append(Dimension(generator))
        # only the inner-most generator needs to have bounds calculated
        generators[-1].prepare_bounds()

        for excluder in excluders:
            axis_1, axis_2 = excluder.scannables
            gen_1 = [g for g in generators if axis_1 in g.axes][0]
            gen_2 = [g for g in generators if axis_2 in g.axes][0]
            gen_diff = generators.index(gen_1) \
                - generators.index(gen_2)
            if gen_diff < -1 or gen_diff > 1:
                raise ValueError(
                    "Excluders must be defined on axes that are adjacent in " \
                        "generator order")

            # merge dimensions if region spans two
            dim_1 = [i for i in self.dimensions if axis_1 in i.axes][0]
            dim_2 = [i for i in self.dimensions if axis_2 in i.axes][0]
            dim_diff = self.dimensions.index(dim_1) \
                - self.dimensions.index(dim_2)
            if dim_diff == 1:
                dim_1, dim_2 = dim_2, dim_1
                dim_diff = -1
            if dim_1.alternate != dim_2.alternate \
                    and dim_1 is not self.dimensions[0]:
                raise ValueError(
                    "Generators tied by regions must have the same " \
                            "alternate setting")
            # merge "inner" into "outer"
            if dim_diff == -1:
                # dim_1 is "outer" - preserves axis ordering
                new_dim = Dimension.merge_dimensions(dim_1, dim_2)
                self.dimensions[self.dimensions.index(dim_1)] = new_dim
                self.dimensions.remove(dim_2)
                dim = new_dim
            else:
                dim = dim_1

            dim.apply_excluder(excluder)

        self.size = 1
        for dim in self.dimensions:
            self._dim_meta[dim] = {}
            mask = dim.create_dimension_mask()
            indices = np.nonzero(mask)[0]
            if len(indices) == 0:
                raise ValueError("Regions would exclude entire scan")
            self.size *= len(indices)
            self._dim_meta[dim]["mask"] = mask
            self._dim_meta[dim]["indices"] = indices

        repeat = self.size
        tile = 1
        for dim in self.dimensions:
            dim_length = len(self._dim_meta[dim]["indices"])
            repeat /= dim_length
            self._dim_meta[dim]["tile"] = tile
            self._dim_meta[dim]["repeat"] = repeat
            tile *= dim_length

        for dim in self.dimensions:
            tile = 1
            repeat = dim.size
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
            indices = self._dim_meta[dim]["indices"]
            i = int(n // self._dim_meta[dim]["repeat"])
            i %= len(indices)
            k = indices[i]
            dim_reverse = False
            if dim.alternate and kc % 2 == 1:
                i = len(indices) - i - 1
                dim_reverse = True
            kc *= len(indices)
            kc += k
            k = indices[i]
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
                    if g is self.generators[-1]:
                        point.lower[axis] = g.bounds[axis][j_lower]
                        point.upper[axis] = g.bounds[axis][j_upper]
                    else:
                        point.lower[axis] = g.positions[axis][j]
                        point.upper[axis] = g.positions[axis][j]
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
        return cls(generators, excluders, mutators)
