from scanpointgenerator import LineGenerator, NestedGenerator, plot_generator
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.circular_roi import CircularROI
from scanpointgenerator.rastergenerator import RasterGenerator
from scanpointgenerator.gridgenerator import GridGenerator
from scanpointgenerator.spiralgenerator import SpiralGenerator
from scanpointgenerator.lissajousgenerator import LissajousGenerator
from scanpointgenerator.factory import Factory


def test_check():

    xs = LineGenerator("x", "mm", 0, 1, 5)
    ys = LineGenerator("y", "mm", 1, 1, 4)
    gen = NestedGenerator(ys, xs, alternate_direction=True)

    rectangle = RectangularROI([2.0, 2.5], 3.0, 2.0)

    plot_generator(gen, rectangle)


def raster_circle_check():

    bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
    inner_scan = dict(name='x', units='mm', step=2.0)
    outer_scan = dict(name='y', units='mm', step=1.0)

    gen = RasterGenerator(bounding_box, inner_scan, outer_scan, alternate_direction=True)

    circle = CircularROI([2.0, 1.0], 2.0)

    plot_generator(gen, circle)


def grid_circle_check():

    bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
    inner_scan = dict(name='x', units='mm', num=4)
    outer_scan = dict(name='y', units='mm', num=3)

    gen = GridGenerator(bounding_box, inner_scan, outer_scan, alternate_direction=True)

    circle = CircularROI([2.0, 1.0], 2.0)

    cut_out = Factory(gen, circle)

    plot_generator(gen, circle)
    plot_generator(cut_out, circle)


def spiral_check():

    gen = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 5.0)
    plot_generator(gen)


def spiral_rectangle_check():

    gen = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 100.0, 100.0)
    rectangle = RectangularROI([0.0, 0.0], 100.0, 100.0)

    cut_out = Factory(gen, rectangle)

    plot_generator(cut_out, rectangle)


def lissajous_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    gen = LissajousGenerator(['x', 'y'], "mm", bounding_box, 8, [1, 2])

    plot_generator(gen)


# test_check()
# raster_circle_check()
# grid_circle_check()
# spiral_check()
# spiral_rectangle_check()
lissajous_check()
