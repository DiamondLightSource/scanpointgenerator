###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import logging

from annotypes import Serializable, Anno, Union, Array, Sequence, \
    deserialize_object

from scanpointgenerator.compat import range_, np
from scanpointgenerator.core.dimension import Dimension
from scanpointgenerator.core.generator import Generator
from scanpointgenerator.core.point import Point
from scanpointgenerator.core.excluder import Excluder
from scanpointgenerator.excluders.roiexcluder import ROIExcluder
from scanpointgenerator.core.mutator import Mutator
from scanpointgenerator.rois import RectangularROI
from scanpointgenerator.generators import LineGenerator, StaticPointGenerator

with Anno("List of Generators to nest"):
    AGenerators = Array[Generator]
UGenerators = Union[AGenerators, Sequence[Generator], Generator]
with Anno("List of Excluders to filter points by"):
    AExcluders = Array[Excluder]
UExcluders = Union[AExcluders, Sequence[Excluder], Excluder]
with Anno("List of Mutators to apply to each point"):
    AMutators = Array[Mutator]
UMutators = Union[AMutators, Sequence[Mutator], Mutator]
with Anno("Point durations in seconds (-1 for variable)"):
    ADuration = float
with Anno("Make points continuous (set upper/lower bounds)"):
    AContinuous = bool
with Anno("Time delay after each point"):
    ADelay = float


@Generator.register_subclass(
    "scanpointgenerator:generator/CompoundGenerator:1.0")
class CompoundGenerator(Serializable):
    """Nest N generators, apply exclusion regions to relevant generator pairs
    and apply any mutators before yielding points"""

    def __init__(self,
                 generators,  # type: UGenerators
                 excluders=(),  # type: UExcluders
                 mutators=(),  # type: UMutators
                 duration=-1,  # type: ADuration
                 continuous=True,  # type: AContinuous
                 delay_after=0  # type: ADelay
                 ):
        # type: (...) -> None
        self.size = 0
        """int: Final number of points to be generated -
        valid only after calling prepare"""
        self.shape = None
        """tuple(int): Final shape of the scan -
        valid only after calling prepare"""
        self.dimensions = []
        """list(Dimension): Dimension instances -
        valid only after calling prepare"""

        self.generators = AGenerators(
            [deserialize_object(g, Generator) for g in generators])
        self.excluders = AExcluders(
            [deserialize_object(e, Excluder) for e in excluders])
        self.mutators = AMutators(
            [deserialize_object(m, Mutator) for m in mutators])
        self.duration = ADuration(duration)
        self.continuous = AContinuous(continuous)
        self.axes = []
        self.units = {}
        self._dim_meta = {}
        self._prepared = False
        self.delay_after = ADelay(delay_after)
        if self.delay_after < 0.0:
            self.delay_after = 0.0


        for generator in self.generators:
            logging.debug("Generator passed to Compound init")
            logging.debug(generator.to_dict())
            self.axes += generator.axes
            self.units.update(generator.axis_units())
        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated")


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
                        gen_1.axes, gen_1.units, [points_1[0]], [points_1[-1]],
                        len(points_1), gen_1.alternate)
                    new_gen2 = LineGenerator(
                        gen_2.axes, gen_2.units, [points_2[0]], [points_2[-1]],
                        len(points_2), gen_2.alternate)
                    generators[generators.index(gen_1)] = new_gen1
                    generators[generators.index(gen_2)] = new_gen2
                    # Remove Excluder as it is now empty
                    excluders.remove(excluder_)

        for generator in generators:
            generator.prepare_positions()
            self.dimensions.append(Dimension([generator]))
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

        # determine which point to extract from each dimension
        # handling the fact that some dimensions "alternate"
        for dim in self.dimensions:
            k = int(n // self._dim_meta[dim]["repeat"])

            dim_runs = k // dim.size
            dim_idx = k % dim.size
            idx = dim.indices[dim_idx]
            dim_in_reverse = dim.alternate and dim_runs % 2 == 1
            if dim_in_reverse:
                dim_idx = dim.size - dim_idx - 1

            dim_positions = dim.get_point(dim_idx)
            point.positions.update(dim_positions)
            if dim is self.dimensions[-1]:
                lower, upper = dim.get_bounds(dim_idx, dim_in_reverse)
                point.lower.update(lower)
                point.upper.update(upper)
            else:
                point.lower.update(dim_positions)
                point.upper.update(dim_positions)
            point.indexes.append(dim_idx)

        point.duration = self.duration
        point.delay_after = self.delay_after
        for m in self.mutators:
            point = m.mutate(point, n)
        return point
