import logging
import numpy as np
from threading import Lock

from scanpointgenerator.compat import range_
from scanpointgenerator.core.generator import Generator
from scanpointgenerator.core.point import Point
from scanpointgenerator.core.excluder import Excluder
from scanpointgenerator.core.mutator import Mutator


@Generator.register_subclass("scanpointgenerator:generator/CompoundGenerator:1.0")
class CompoundGenerator(Generator):
    """Nest N generators, apply exclusion regions to relevant generator pairs
    and apply any mutators before yielding points"""

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
        self.axes_points = {}
        self.axes_points_lower = {}
        self.axes_points_upper = {}
        self.index_dims = []
        self.indexes = []
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
        self.generator_idx_scaling = {}

    def prepare(self):
        self.num = 1
        self.indexes = []
        for generator in self.generators:
            generator.produce_points()
            self.axes_points.update(generator.points)
            self.axes_points_lower.update(generator.points_lower)
            self.axes_points_upper.update(generator.points_upper)
            self.num *= generator.num
            self.index_dims += generator.index_dims

            idx = {"size":generator.num,
                "axes":list(generator.axes),
                "generators":[generator],
                "masks":[],
                "tile":1,
                "repeat":1}
            self.indexes.append(idx)

        for excluder in self.excluders:
            axis_1, axis_2 = excluder.scannables

            #####
            # first check if region spans two indexes - merge if so
            #####
            idx_1 = [i for i in self.indexes if axis_1 in i["axes"]][0]
            idx_2 = [i for i in self.indexes if axis_2 in i["axes"]][0]
            order_diff = self.indexes.index(idx_1) - self.indexes.index(idx_2)
            # merge "inner" into "outer"
            if order_diff < -1 or order_diff > 1:
                raise ValueError(
                    "Excluders must be defined on axes that are adjacent in \
                        generator order")
            if order_diff == 1:
                idx_1, idx_2 = idx_2, idx_1
                order_diff = -1
            if order_diff == -1:
                # idx_1 is "outer" - preserves axis ordering

                # need to appropriately scale the existing masks
                # masks are "tiled" by the size of generators "below" them
                # and their elements are "repeated" by the size of generators
                # above them, so:
                # |mask| * duplicates * repeates == |generators in index|
                scale = 1
                for g in idx_2["generators"]:
                    scale *= g.num
                for m in idx_1["masks"]:
                    m["repeat"] *= scale
                scale = 1
                for g in idx_1["generators"]:
                    scale *= g.num
                for m in idx_2["masks"]:
                    m["tile"] *= scale
                idx_1["masks"] += idx_2["masks"]
                idx_1["axes"] += idx_2["axes"]
                idx_1["generators"] += idx_2["generators"]
                idx_1["size"] *= idx_2["size"]
                self.indexes.remove(idx_2)
            idx = idx_1

            #####
            # generate the mask for this region
            #####
            gen_1 = [g for g in self.generators if axis_1 in g.axes][0]
            gen_2 = [g for g in self.generators if axis_2 in g.axes][0]
            # if gen_1 and gen_2 are different then the outer axis will have to
            # have its elements repeated and the inner axis will have to have
            # itself repeated - need to determine which is the inner axis
            a1_scalef = np.repeat
            a2_scalef = np.tile
            order_diff = self.generators.index(gen_1) \
                - self.generators.index(gen_2)

            if order_diff < -1 or order_diff > 1:
                raise ValueError(
                    "Excluders must be defined on axes that are adjacent in \
                        generator order")
            if order_diff == 1:
                # axis order is reversed - swap "scaling" functions
                a1_scalef, a2_scalef = a2_scalef, a1_scalef
                order_diff = -1

            points_1 = self.axes_points[axis_1]
            points_2 = self.axes_points[axis_2]
            if order_diff == -1:
                points_1 = a1_scalef(points_1, gen_2.num)
                points_2 = a2_scalef(points_2, gen_1.num)

            mask = excluder.create_mask(points_1, points_2)

            #####
            # Add new mask to index
            #####
            tile = 1
            repeat = 1
            found_axis = False
            # tile by product of generators "before"
            # repeat by product of generators "after"
            for g in idx["generators"]:
                if axis_1 in g.axes or axis_2 in g.axes:
                    found_axis = True
                else:
                    if found_axis:
                        repeat *= g.num
                    else:
                        tile *= g.num
            m = {"repeat":repeat, "tile":tile, "mask":mask}
            idx["masks"].append(m)
        # end for excluder in self.excluders
        #####

        tile = 1
        repeat = 1
        #####
        # Generate full index mask and "apply"
        #####
        for idx in self.indexes:
            mask = np.full(idx["size"], True, dtype=np.bool)
            for m in idx["masks"]:
                assert len(m["mask"]) * m["repeat"] * m["tile"] == len(mask), \
                        "Mask lengths are not consistent"
                expanded = np.repeat(m["mask"], m["repeat"])
                expanded = np.tile(expanded, m["tile"])
                mask &= expanded
            idx["mask"] = mask
            idx["indicies"] = np.flatnonzero(mask)
            if len(idx["indicies"]) == 0:
                raise ValueError("Regions would exclude entire scan")
            repeat *= len(idx["indicies"])
        self.num = repeat
        for idx in self.indexes:
            l = len(idx["indicies"])
            repeat /= l
            idx["tile"] = tile
            idx["repeat"] = repeat
            tile *= l

        for idx in self.indexes:
            tile = 1
            repeat = 1
            for g in idx["generators"]:
                repeat *= g.num
            for g in idx["generators"]:
                repeat /= g.num
                d = {"tile":tile, "repeat":repeat}
                tile *= g.num
                self.generator_idx_scaling[g] = d

    def iterator(self):
        # just one axis for now
        for n in range_(self.num):
            yield self.get_point(n)

    def get_point(self, n):
        # how far along each index are we?
        if n >= self.num:
            raise IndexError("Requested point is out of range")
        p = Point()
        for idx in self.indexes:
            i = n // idx["repeat"]
            i %= len(idx["indicies"])
            k = idx["indicies"][i]
            # need point k along each generator in index
            for g in idx["generators"]:
                j = k // self.generator_idx_scaling[g]["repeat"]
                j %= g.num
                for axis in g.axes:
                    p.positions[axis] = g.points[axis][j]
                    p.lower[axis] = g.points_lower[axis][j]
                    p.upper[axis] = g.points_upper[axis][j]
        return p

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
