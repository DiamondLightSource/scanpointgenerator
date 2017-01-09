import logging

from scanpointgenerator.compat import range_, np
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
        self.position_units = {}
        self.index_dims = []
        self.dimensions = []
        self.num = 1
        self.dim_meta = {}
        self.alternate_direction = [g.alternate_direction for g in generators]
        for generator in generators:
            logging.debug("Generator passed to Compound init")
            logging.debug(generator.to_dict())
            if isinstance(generator, self.__class__):
                raise TypeError("CompoundGenerators cannot be nested, nest"
                                "its constituent parts instead")
            self.axes += generator.axes
            self.position_units.update(generator.position_units)
        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated")

        self.generators = generators
        self.generator_dim_scaling = {}

    def prepare(self):
        """
        Prepare data structures and masks required for point generation.
        Must be called before get_point or iterator are called.
        """
        self.dimensions = []
        self.index_dims = []
        self.dim_meta = {}
        self.generator_dim_scaling = {}

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
                valid = np.full(gen_1.num, True, dtype=np.int8)
                valid &= gen_1.positions[axis_1] \
                        <= rect.roi.width + rect.roi.start[0]
                valid &= gen_1.positions[axis_1] >= rect.roi.start[0]
                points_1 = gen_1.positions[axis_1][valid.astype(np.bool)]
                valid = np.full(gen_2.num, True, dtype=np.int8)
                valid &= gen_2.positions[axis_2] \
                        <= rect.roi.height + rect.roi.start[1]
                valid &= gen_2.positions[axis_2] >= rect.roi.start[1]
                points_2 = gen_2.positions[axis_2][valid.astype(np.bool)]
                new_gen1 = LineGenerator(
                    gen_1.name, gen_1.units, points_1[0], points_1[-1],
                    len(points_1), gen_1.alternate_direction)
                new_gen2 = LineGenerator(
                    gen_2.name, gen_2.units, points_2[0], points_2[-1],
                    len(points_2), gen_2.alternate_direction)
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
                            "alternate_direction setting")
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

        self.num = 1
        for dim in self.dimensions:
            self.dim_meta[dim] = {}
            mask = dim.create_dimension_mask()
            indicies = np.nonzero(mask)[0]
            if len(indicies) == 0:
                raise ValueError("Regions would exclude entire scan")
            self.num *= len(indicies)
            self.dim_meta[dim]["mask"] = mask
            self.dim_meta[dim]["indicies"] = indicies
            self.index_dims.append(len(indicies))

        repeat = self.num
        tile = 1
        for dim in self.dimensions:
            dim_length = len(self.dim_meta[dim]["indicies"])
            repeat /= dim_length
            self.dim_meta[dim]["tile"] = tile
            self.dim_meta[dim]["repeat"] = repeat
            tile *= dim_length

        for dim in self.dimensions:
            tile = 1
            repeat = 1
            for g in dim.generators:
                repeat *= g.num
            for g in dim.generators:
                repeat /= g.num
                d = {"tile":tile, "repeat":repeat}
                tile *= g.num
                self.generator_dim_scaling[g] = d

    def iterator(self):
        """
        Iterator yielding generator positions at each scan point

        Yields:
            Point: The next point
        """
        it = (self.get_point(n) for n in range_(self.num))
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

        if n >= self.num:
            raise IndexError("Requested point is out of range")
        point = Point()

        # need to know how far along each dimension we are
        # and, in the case of alternating indicies, how
        # many times we've run through them
        kc = 0 # the "cumulative" k for each dimension
        for dim in self.dimensions:
            indicies = self.dim_meta[dim]["indicies"]
            i = int(n // self.dim_meta[dim]["repeat"])
            i %= len(indicies)
            k = indicies[i]
            dim_reverse = False
            if dim.alternate and kc % 2 == 1:
                i = len(indicies) - i - 1
                dim_reverse = True
            kc *= len(indicies)
            kc += k
            k = indicies[i]
            # need point k along each generator in dimension
            # in alternating case, need to sometimes go backward
            point.indexes.append(i)
            for g in dim.generators:
                j = int(k // self.generator_dim_scaling[g]["repeat"])
                r = int(j // g.num)
                j %= g.num
                j_lower = j
                j_upper = j + 1
                if dim.alternate and g is not dim.generators[0] and r % 2 == 1:
                    # the top level generator's direction is handled by
                    # the fact that the reverse direction was appended
                    j = g.num - j - 1
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

class Dimension(object):
    """A collapsed set of generators joined by excluders"""
    def __init__(self, generator):
        self.axes = list(generator.axes)
        self.generators = [generator]
        self.size = generator.num
        self.masks = []
        self.alternate = generator.alternate_direction

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
            points_x = np.repeat(points_x, gen_outer.num)
            points_y = np.append(points_y, points_y[::-1])
            points_y = np.tile(points_y, gen_inner.num)
        elif gen_inner is not gen_outer:
            points_x = np.repeat(points_x, gen_outer.num)
            points_y = np.tile(points_y, gen_inner.num)
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
                    repeat *= g.num
                else:
                    tile *= g.num

        m = {"repeat":repeat, "tile":tile, "mask":mask}
        self.masks.append(m)

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
        for m in self.masks:
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
        inner_masks = [m.copy() for m in inner.masks]
        outer_masks = [m.copy() for m in outer.masks]
        scale = 1
        for g in inner.generators:
            scale *= g.num
        for m in outer_masks:
            m["repeat"] *= scale
        scale = 1
        for g in outer.generators:
            scale *= g.num
        for m in inner_masks:
            m["tile"] *= scale
        dim.masks = outer_masks + inner_masks
        dim.axes = outer.axes + inner.axes
        dim.generators = outer.generators + inner.generators
        dim.alternate = outer.alternate or inner.alternate
        dim.size = outer.size * inner.size
        return dim
