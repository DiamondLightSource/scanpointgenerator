from scanpointgenerator import LineGenerator, NestedGenerator
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.circular_roi import CircularROI
from scanpointgenerator.gridgenerator import GridGenerator
from scanpointgenerator.spiralgenerator import SpiralGenerator
from scanpointgenerator.lissajousgenerator import LissajousGenerator
from scanpointgenerator.randomoffsetgenerator import RandomOffsetGenerator
from scanpointgenerator.maskedgenerator import MaskedGenerator
from plotgenerator2 import plot_generator

from pkg_resources import require
require('matplotlib')
require('numpy')
require('scipy')


def test_check():

    xs = LineGenerator("x", "mm", 0, 1, 5)
    ys = LineGenerator("y", "mm", 1, 1, 4)
    gen = NestedGenerator(ys, xs, alternate_direction=True)

    rectangle = RectangularROI([2.0, 2.5], 3.0, 2.0)

    plot_generator(gen, rectangle)


def grid_circle_check():

    bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
    inner_scan = dict(name='x', units='mm', num=4)
    outer_scan = dict(name='y', units='mm', num=3)

    gen = GridGenerator(bounding_box, inner_scan, outer_scan, alternate_direction=True)

    circle = CircularROI([2.0, 1.0], 2.0)

    cut_out = MaskedGenerator(gen, circle)

    plot_generator(gen, circle)
    plot_generator(cut_out, circle)


def spiral_check():

    gen = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 10.0)
    plot_generator(gen)


def spiral_rectangle_check():

    gen = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 100.0, 100.0)
    rectangle = RectangularROI([0.0, 0.0], 100.0, 100.0)

    cut_out = MaskedGenerator(gen, rectangle)

    plot_generator(cut_out, rectangle)


def lissajous_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    gen = LissajousGenerator(['x', 'y'], "mm", bounding_box, 2)

    plot_generator(gen)


def line_2d_check():

    gen = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)

    plot_generator(gen)


def random_offset_check():

    bounding_box = dict(centre=[2.0, 1.0], width=4.0, height=2.0)
    inner_scan = dict(name='x', units='mm', num=4)
    outer_scan = dict(name='y', units='mm', num=3)

    line = GridGenerator(bounding_box, inner_scan, outer_scan, alternate_direction=True)
    gen = RandomOffsetGenerator(line, 2, dict(x=0.25, y=0.25))

    plot_generator(gen)


# test_check()
# raster_circle_check()
# grid_circle_check()
spiral_check()
# spiral_rectangle_check()
# lissajous_check()
# line_2d_check()
# random_offset_check()
