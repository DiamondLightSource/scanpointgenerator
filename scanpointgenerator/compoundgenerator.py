from collections import OrderedDict

from generator import Generator
from scanregion import ScanRegion
from point import Point


@Generator.register_subclass("CompoundGenerator")
class CompoundGenerator(Generator):
    """Nest N generators and apply filter regions to relevant generator pairs"""

    def __init__(self, generators, regions):
        """
        Args:
            generators(list(Generator)): List of Generators to nest
            regions(list(ScanRegion)): List of regions to filter points by
        """

        self.generators = generators
        self.regions = regions

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

    def iterator(self):

        for point_num in xrange(self.num_points):

            point = Point()
            for gen_index, points in enumerate(self.point_sets):
                axis_period = self.periods[gen_index]
                axis_length = self.lengths[gen_index]

                point_index = \
                    (point_num / (axis_period / axis_length)) % axis_length

                loop_number = point_num / axis_period
                if self.alternate_direction[gen_index] and loop_number % 2:
                    point_index = (axis_length - 1) - point_index
                    reverse = True
                else:
                    reverse = False

                current_point = self.point_sets[gen_index][point_index]

                if gen_index == 0:  # If innermost, generator use bounds
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
        for generator in self.generators:
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
