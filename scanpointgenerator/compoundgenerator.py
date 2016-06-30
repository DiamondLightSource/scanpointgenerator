from collections import OrderedDict

from scanpointgenerator import Generator
from scanpointgenerator.excluder import Excluder
from scanpointgenerator.mutator import Mutator
from scanpointgenerator import Point


@Generator.register_subclass("CompoundGenerator")
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

        self.generators = generators
        self.excluders = excluders
        self.mutators = mutators

        self.num_points = 1
        self.periods = []
        self.alternate_direction = []
        self.point_sets = []
        for generator in self.generators:
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
                axis_length = self.index_dims[gen_index]

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

    def _filtered_base_iterator(self):
        """
        Iterator to filter out points based on Excluders

        Yields:
            Point: Filtered points
        """

        for point in self._base_iterator():
            if self.contains_point(point):
                yield point

    def iterator(self):
        """
        Top level iterator to mutate points and yield them

        Yields:
            Point: Mutated points
        """

        iterator = self._filtered_base_iterator()
        for mutator in self.mutators:
            iterator = mutator.mutate(iterator)

        for point in iterator:
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

        for excluder in self.excluders:
            coord_1 = point.positions[excluder.scannables[0]]
            coord_2 = point.positions[excluder.scannables[1]]
            coordinate = [coord_1, coord_2]

            if not excluder.roi.contains_point(coordinate):
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

        d['excluders'] = []
        for excluder in self.excluders:
            d['excluders'].append(excluder.to_dict())

        d['mutators'] = []
        for mutator in self.mutators:
            d['mutators'].append(mutator.to_dict())

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

        excluders = []
        for excluder in d['excluders']:
            excluders.append(Excluder.from_dict(excluder))

        mutators = []
        for mutator in d['mutators']:
            mutators.append(Mutator.from_dict(mutator))

        return cls(generators, excluders, mutators)
