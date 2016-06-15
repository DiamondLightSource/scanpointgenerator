from linegenerator import LineGenerator
from compoundgenerator import NestedGenerator


class GridGenerator(NestedGenerator):

    def __init__(self, box, inner_scan, outer_scan, alternate_direction=False):

        left_edge = box['centre'][0] - box['width']/2.0
        right_edge = box['centre'][0] + box['width']/2.0
        top_edge = box['centre'][1] - box['height']/2.0
        bottom_edge = box['centre'][1] + box['height']/2.0

        inner_generator = LineGenerator(inner_scan['name'],
                                        inner_scan['units'], left_edge,
                                        right_edge, inner_scan['num'])

        outer_generator = LineGenerator(outer_scan['name'],
                                        outer_scan['units'], top_edge,
                                        bottom_edge, outer_scan['num'])

        super(GridGenerator, self).__init__(outer_generator, inner_generator,
                                            alternate_direction=alternate_direction)
