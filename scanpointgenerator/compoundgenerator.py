from collections import OrderedDict

from scanpointgenerator import Generator
from scanpointgenerator.excluder import Excluder
from scanpointgenerator.mutator import Mutator
from scanpointgenerator import Point


@Generator.register_subclass("CompoundGenerator")
class CompoundGenerator(Generator):
    """Nest N generators and apply filter regions to relevant generator pairs"""

    def __init__(self, generators, mutators, excluders):
        """
        Args:
            generators(list(Generator)): List of Generators to nest
            mutators(list(Mutator)): List of Processors to apply to each point
            excluders(list(Excluder)): List of regions to filter points by
        """

        self.generators = generators
        self.mutators = mutators
        self.excluders = excluders

        self.lengths = []
        self.num_points = 1
        self.periods = []
        self.alternate_direction = []
        self.point_sets = []
        for generator in self.generators:
            self.lengths.append(generator.num)
            self.num_points *= generator.num
            self.periods.append(self.num_points)
            self.alternate_direction.append(generator.alternate_direction)
            self.point_sets.append(list(generator.iterator()))

        self.position_units = generators[0].position_units.copy()
        for generator in generators[1:]:
            self.position_units.update(generator.position_units)

        self.index_dims = []
        for generator in generators:
            self.index_dims += generator.index_dims

        self.index_names = []
        for generator in generators:
            self.index_names += generator.index_names

    def _base_iterator(self):
        """
        Iterator to generate points by nesting each generator in self.generators

        Yields:
            Point: Base points
        """

        for point_num in range(self.num_points):

            point = Point()
            for gen_index, points in enumerate(self.point_sets):
                axis_period = self.periods[gen_index]
                axis_length = self.lengths[gen_index]

                point_index = \
                    (point_num / (axis_period / axis_length)) % axis_length
                loop_number = point_num / axis_period

                # Floor floats to ints for indexing
                point_index = int(point_index)
                loop_number = int(loop_number)
                if self.alternate_direction[gen_index] and loop_number % 2:
                    point_index = (axis_length - 1) - point_index
                    reverse = True
                else:
                    reverse = False

                current_point = self.point_sets[gen_index][point_index]

                if gen_index == 0:  # If innermost generator, use bounds
                    point.positions.update(current_point.positions)
                    if reverse:  # Swap bounds if reversing
                        point.upper.update(current_point.lower)
                        point.lower.update(current_point.upper)
                    else:
                        point.upper.update(current_point.upper)
                        point.lower.update(current_point.lower)
                else:
                    point.positions.update(current_point.positions)
                    point.upper.update(current_point.positions)
                    point.lower.update(current_point.positions)

                point.indexes += current_point.indexes

            yield point

    def _mutated_base_iterator(self):
        """
        Iterator to mutate the points generated from the nest of generators
        using mutators in self. mutators, if there are any

        Yields:
            Point: Mutated points
        """

        iterator = self._base_iterator()
        # itertools...
        for mutator in self.mutators:
            iterator = mutator.mutate(iterator)

        for point in iterator:
                yield point

    def iterator(self):
        """
        Top level iterator to filter points based on region of interest

        Yields:
            Point: Filtered points
        """

        for point in self._mutated_base_iterator():
            if self.contains_point(point):
                yield point

    def contains_point(self, point):
        """
        Filter a Point through all ScanRegions

        Args:
            point(Point): Point to check

        Returns:
            bool: Whether point is contained by all ScanRegions
        """

        contains_point = True

        for region in self.excluders:
            coord_1 = point.positions[region.scannables[0]]
            coord_2 = point.positions[region.scannables[1]]
            coordinate = [coord_1, coord_2]

            if not region.roi.contains_point(coordinate):
                contains_point = False
                break

        return contains_point

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d['type'] = "CompoundGenerator"

        d['generators'] = []
        for generator in self.generators:
            d['generators'].append(generator.to_dict())

        d['mutators'] = []
        for mutator in self.mutators:
            d['mutators'].append(mutator.to_dict())

        d['regions'] = []
        for region in self.excluders:
            d['regions'].append(region.to_dict())

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

        generators = []
        for generator in d['generators']:
            generators.append(Generator.from_dict(generator))

        mutators = []
        for mutator in d['mutators']:
            mutators.append(Mutator.from_dict(mutator))

        regions = []
        for region in d['regions']:
            regions.append(Excluder.from_dict(region))

        return cls(generators, mutators, regions)
