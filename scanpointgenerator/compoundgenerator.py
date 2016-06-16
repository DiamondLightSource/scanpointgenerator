from collections import OrderedDict

from generator import Generator
from scanregion import ScanRegion
from point import Point


@Generator.register_subclass("CompoundGenerator")
class CompoundGenerator(Generator):
    """Nest N generators and apply filter regions to relevant generator pairs"""

    def __init__(self, generator_list, regions):
        """
        Args:
            generator_list(list(Generator)): List of Generators to nest
            regions(list(ScanRegion)): List of regions to filter points by
        """

        self.generators = OrderedDict()
        for generator in generator_list:
            self.generators[generator.name[0]] = generator

        self.regions = regions

        self.inner = generator_list[0].name[0]
        self.num_points = 1
        self.axis_lengths = {}
        self.repeat_periods = {}
        self.current_axis_indexes = {}
        self.alternate_direction = {}
        for axis, generator in self.generators.items():
            self.num_points *= generator.num
            self.axis_lengths[axis] = generator.num
            self.repeat_periods[axis] = self.num_points
            self.current_axis_indexes[axis] = 0
            self.alternate_direction[axis] = generator.alternate_direction

        self.current_axis_points = {}
        self.iterators = {}

        self.position_units = generator_list[0].position_units.copy()
        for generator in generator_list[1:]:
            self.position_units.update(generator.position_units)

        self.index_dims = []
        for generator in generator_list:
            self.index_dims += generator.index_dims

        self.index_names = []
        for generator in generator_list:
            self.index_names += generator.index_names

    def iterator(self):

        for point_num in xrange(self.num_points):

            point = Point()
            for axis, generator in self.generators.items():
                repeat_period = self.repeat_periods[axis]
                axis_length = self.axis_lengths[axis]

                if point_num == 0:
                    new_index = 0
                else:
                    new_index = point_num / (repeat_period / axis_length) % axis_length

                # If start of axis, reset iterator and index for axis
                if new_index == 0:

                    loop_number = point_num / repeat_period
                    if self.alternate_direction[axis] and loop_number % 2:
                        generator.reverse = True
                    else:
                        generator.reverse = False
                    self.iterators[axis] = generator.iterator()

                    self.current_axis_points[axis] = self.iterators[axis].next()
                    self.current_axis_indexes[axis] = 0

                # Else if axis index has increased, get next point
                elif new_index == self.current_axis_indexes[axis] + 1:
                    self.current_axis_indexes[axis] = new_index
                    self.current_axis_points[axis] = self.iterators[axis].next()

                # Else just use the same point as last time

                current_point = self.current_axis_points[axis]
                if axis == self.inner:
                    point.positions[axis] = current_point.positions[axis]
                    point.upper[axis] = current_point.upper[axis]
                    point.lower[axis] = current_point.lower[axis]
                else:
                    point.positions[axis] = current_point.positions[axis]
                    point.upper[axis] = current_point.positions[axis]
                    point.lower[axis] = current_point.positions[axis]

                point.indexes += current_point.indexes

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

        for region in self.regions:
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
        for generator in self.generators.values():
            d['generators'].append(generator.to_dict())

        d['regions'] = []
        for region in self.regions:
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

        regions = []
        for region in d['regions']:
            regions.append(ScanRegion.from_dict(region))

        return cls(generators, regions)
