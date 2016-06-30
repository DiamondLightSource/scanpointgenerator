from scanpointgenerator import LineGenerator, CompoundGenerator
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.circular_roi import CircularROI
from scanpointgenerator.spiralgenerator import SpiralGenerator
from scanpointgenerator.lissajousgenerator import LissajousGenerator
from scanpointgenerator.randomoffsetmutator import RandomOffsetMutator
from scanpointgenerator.excluder import Excluder
from plotgenerator2 import plot_generator

from pkg_resources import require
require('matplotlib')
require('numpy')
require('scipy')


def grid_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([x, y], [], [])

    plot_generator(gen)


def grid_circle_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circle = CircularROI([2.0, 1.0], 2.0)
    excluder = Excluder(circle, ['x', 'y'])

    gen = CompoundGenerator([x, y], [], [scan_region])

    plot_generator(gen, circle)


def spiral_check():

    gen = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 10.0)
    plot_generator(gen)


def spiral_rectangle_check():

    spiral = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 10.0)
    rectangle = RectangularROI([0.0, 0.0], 10.0, 10.0)
    excluder = Excluder(rectangle, ['x', 'y'])

    gen = CompoundGenerator([spiral], [], [scan_region])

    plot_generator(gen, rectangle)


def lissajous_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    gen = LissajousGenerator(['x', 'y'], "mm", bounding_box, 2)

    plot_generator(gen)


def lissajous_rectangle_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    lissajous = LissajousGenerator(['x', 'y'], "mm", bounding_box, 2)
    rectangle = RectangularROI([0.0, 0.0], 0.8, 0.8)
    excluder = Excluder(rectangle, ['x', 'y'])

    gen = CompoundGenerator([lissajous], [], [scan_region])

    plot_generator(gen)


def line_2d_check():

    gen = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)

    plot_generator(gen)


def random_offset_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    mutator = RandomOffsetMutator(2, dict(x=0.25, y=0.25))

    gen = CompoundGenerator([x, y], [mutator], [])

    plot_generator(gen)

    gen = CompoundGenerator([x, y], [mutator, mutator], [])

    plot_generator(gen)

    gen = CompoundGenerator([x, y], [mutator, mutator, mutator], [])

    plot_generator(gen)

    gen = CompoundGenerator([x, y], [mutator, mutator, mutator, mutator, mutator], [])

    plot_generator(gen)


grid_check()
grid_circle_check()
spiral_check()
spiral_rectangle_check()
lissajous_check()
lissajous_rectangle_check()
line_2d_check()
# random_offset_check()
