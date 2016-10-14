import logging
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

        self.generators = generators
        self.excluders = excluders
        self.mutators = mutators

        self.alternate_direction = []
        self.point_sets = []
        self.index_dims = []
        self.index_names = []
        self.axes = []
        self.position_units = {}

        for generator in self.generators:
            logging.debug("Generator passed to Compound init")
            logging.debug(generator.to_dict())

            if isinstance(generator, self.__class__):
                raise TypeError("CompoundGenerators cannot be nested, nest"
                                "its constituent parts instead")

            self.alternate_direction.append(generator.alternate_direction)
            self.point_sets.append(list(generator.iterator()))
            self.axes += generator.axes

            self.index_dims += generator.index_dims
            self.index_names += generator.index_names
            self.position_units.update(generator.position_units)

        self.num = 1
        self.periods = []
        for generator in self.generators[::-1]:
            self.num *= generator.num
            self.periods.insert(0, self.num)

        logging.debug("CompoundGenerator periods")
        logging.debug(self.periods)

        if self.excluders:  # Calculate number of remaining points and flatten
                            # index dimensions
            remaining_points = 0
            for _ in self._filtered_base_iterator():
                # TODO: Faster with enumerate()?
                remaining_points += 1
            self.index_dims = [remaining_points]
            self.num = remaining_points

        if len(self.axes) != len(set(self.axes)):
            raise ValueError("Axis names cannot be duplicated; given %s" %
                             self.index_names)

        # These are set when using the get_point() interface
        self._cached_iterator = None
        self._cached_points = []
        self._cached_lock = Lock()

    def _get_sub_point(self, gen_index, point_num):
        points = self.point_sets[gen_index]
        axis_period = self.periods[gen_index]
        axis_length = len(points)
        # Can't use index_dims in case they have been flattened
        # by an excluder

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

        sub_point = points[point_index]

        return reverse, sub_point

    def _base_iterator(self):
        """
        Iterator to generate points by nesting each generator in self.generators

        Yields:
            Point: Base points
        """
        num_point_sets = len(self.point_sets)
        for point_num in range_(self.num):
            point = Point()
            for gen_index in range_(num_point_sets - 1):
                reverse, sub_point = self._get_sub_point(gen_index, point_num)

                # Outer indexes use positions
                point.positions.update(sub_point.positions)
                point.upper.update(sub_point.positions)
                point.lower.update(sub_point.positions)
                point.indexes += sub_point.indexes

            # If innermost generator, use bounds
            reverse, sub_point = self._get_sub_point(
                num_point_sets - 1, point_num)
            point.positions.update(sub_point.positions)
            if reverse:  # Swap bounds if reversing
                point.upper.update(sub_point.lower)
                point.lower.update(sub_point.upper)
            else:
                point.upper.update(sub_point.upper)
                point.lower.update(sub_point.lower)
            point.indexes += sub_point.indexes

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
        if self.excluders:
            iterator = self._filtered_base_iterator()
        else:
            iterator = self._base_iterator()

        for mutator in self.mutators:
            iterator = mutator.mutate(iterator)

        if self.excluders:
            point_index = 0
            for point in iterator:
                point.indexes = [point_index]
                point_index += 1
                yield point
        else:
            for point in iterator:
                yield point

    def contains_point(self, point):
        """
        Filter a Point through all Excluders

        Args:
            point(Point): Point to check

        Returns:
            bool: Whether point is contained by all Excluders
        """

        contains_point = True

        for excluder in self.excluders:
            if not excluder.contains_point(point.positions):
                contains_point = False
                break

        return contains_point

    def get_point(self, num):
        # This is the only thread safe function in scanpointgenerator
        if self._cached_iterator is None:
            self._cached_iterator = self.iterator()

        if num >= len(self._cached_points):
            # Generate some more points and cache them
            try:
                self._cached_lock.acquire()
                # Get npoints again in case someone else added them
                npoints = len(self._cached_points)
                for i in range(num - npoints + 1):
                    self._cached_points.append(next(self._cached_iterator))
            except:
                self._cached_lock.release()
                raise
            else:
                self._cached_lock.release()
        return self._cached_points[num]

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = dict()
        d['typeid'] = self.typeid

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
