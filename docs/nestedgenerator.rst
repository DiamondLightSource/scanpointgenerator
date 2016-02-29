Nested Generator
================

.. module:: scanpointgenerator

.. autoclass:: NestedGenerator
    :members:


Raster Scan Example
-------------------

This scan will create an outer "y" line scan with 4 points, then nest an "x"
line scan inside it with 5 points.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, NestedGenerator, plot_generator

    xs = LineGenerator("x", "mm", 0, 0.1, 5)
    ys = LineGenerator("y", "mm", 1, 0.1, 4)
    gen = NestedGenerator(ys, xs)
    plot_generator(gen)


Snake Scan Example
------------------

This scan will create an outer "y" line scan with 4 points, then nest an "x"
line scan inside it with 5 points. On every second row, the "x" line scan will
be run in reverse to give a snake scan.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, NestedGenerator, plot_generator

    xs = LineGenerator("x", "mm", 0, 0.1, 5)
    ys = LineGenerator("y", "mm", 1, 0.1, 4)
    gen = NestedGenerator(ys, xs, snake=True)
    plot_generator(gen)
