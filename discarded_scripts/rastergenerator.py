from linegenerator_step import StepLineGenerator
from nestedgenerator import NestedGenerator


class RasterGenerator(NestedGenerator):

    def __init__(self, box, inner_scan, outer_scan, alternate_direction=False):

        left_edge = box['centre'][0] - box['width']/2.0
        right_edge = box['centre'][0] + box['width']/2.0
        top_edge = box['centre'][1] - box['height']/2.0
        bottom_edge = box['centre'][1] + box['height']/2.0

        inner_generator = StepLineGenerator(inner_scan['name'],
                                            inner_scan['units'], left_edge,
                                            right_edge, inner_scan['step'])

        outer_generator = StepLineGenerator(outer_scan['name'],
                                            outer_scan['units'], top_edge,
                                            bottom_edge, outer_scan['step'])

        super(RasterGenerator, self).__init__(outer_generator, inner_generator, alternate_direction=alternate_direction)
