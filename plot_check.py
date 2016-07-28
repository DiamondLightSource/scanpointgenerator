from scanpointgenerator import LineGenerator, CompoundGenerator
from scanpointgenerator.rectangular_roi import RectangularROI
from scanpointgenerator.circular_roi import CircularROI
from scanpointgenerator.spiralgenerator import SpiralGenerator
from scanpointgenerator.lissajousgenerator import LissajousGenerator
from scanpointgenerator.randomoffsetmutator import RandomOffsetMutator
from scanpointgenerator.excluder import Excluder
from scanpointgenerator.plotgenerator import plot_generator

from pkg_resources import require
require('matplotlib')
require('numpy')
require('scipy')


def grid_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([y, x], [], [])

    plot_generator(gen)


def grid_circle_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circle = Excluder(CircularROI([2.0, 1.0], 2.0), ['x', 'y'])
    gen = CompoundGenerator([y, x], [circle], [])

    plot_generator(gen, circle)


def spiral_check():

    spiral = SpiralGenerator("XYSpiral", "mm", [0.0, 0.0], 10.0)
    gen = CompoundGenerator([spiral], [], [])

    plot_generator(gen)


def spiral_rectangle_check():

    spiral = SpiralGenerator("XYSpiral", "mm", [0.0, 0.0], 10.0)
    rectangle = Excluder(RectangularROI([0.0, 0.0], 10.0, 10.0), ["XYSpiral_X", "XYSpiral_Y"])
    gen = CompoundGenerator([spiral], [rectangle], [])

    plot_generator(gen, rectangle)


def lissajous_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    lissajous = LissajousGenerator("XYLissajous", "mm", bounding_box, 2)
    gen = CompoundGenerator([lissajous], [], [])

    plot_generator(gen)


def lissajous_rectangle_check():

    bounding_box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    lissajous = LissajousGenerator("XYLissajous", "mm", bounding_box, 2)
    rectangle = Excluder(RectangularROI([0.0, 0.0], 0.8, 0.8), ["XYLissajous_X", "XYLissajous_Y"])
    gen = CompoundGenerator([lissajous], [rectangle], [])

    plot_generator(gen, rectangle)


def line_2d_check():

    line = LineGenerator("XYLine", "mm", [1.0, 2.0], [5.0, 10.0], 5)
    gen = CompoundGenerator([line], [], [])

    plot_generator(gen)


def random_offset_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    mutator = RandomOffsetMutator(2, dict(x=0.25, y=0.25))

    gen = CompoundGenerator([y, x], [], [mutator])

    plot_generator(gen)

    gen = CompoundGenerator([y, x], [], [mutator, mutator])

    plot_generator(gen)

    gen = CompoundGenerator([y, x], [], [mutator, mutator, mutator])

    plot_generator(gen)

    gen = CompoundGenerator([y, x], [], [mutator, mutator, mutator, mutator, mutator])

    plot_generator(gen)


def serialise_grid_check():

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)

    gen = CompoundGenerator([y, x], [], [])

    plot_generator(gen)

    gen = gen.to_dict()
    print(gen)
    gen = CompoundGenerator.from_dict(gen)

    plot_generator(gen)

grid_check()
grid_circle_check()
spiral_check()
spiral_rectangle_check()
lissajous_check()
lissajous_rectangle_check()
line_2d_check()
random_offset_check()
serialise_grid_check()
