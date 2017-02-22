.. _compoundgenerator:

Compound Generator
==================

.. module:: scanpointgenerator

.. autoclass:: CompoundGenerator
    :members:


Raster Scan Example
-------------------

This scan will create an outer "y" line scan with 4 points, then nest an "x"
line scan inside it with 5 points.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate_direction=False)
    ys = LineGenerator("y", "mm", 0.0, 0.5, 4)
    gen = CompoundGenerator([ys, xs], [], [])
    plot_generator(gen)


Snake Scan Example
------------------

This scan will create an outer "y" line scan with 4 points, then nest an "x"
line scan inside it with 5 points. On every second row, the "x" line scan will
be run in reverse to give a snake scan.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate_direction=True)
    ys = LineGenerator("y", "mm", 0.0, 0.5, 4)
    gen = CompoundGenerator([ys, xs], [], [])
    plot_generator(gen)


.. _compoundgenerator_restrictions:

Restrictions
------------

:ref:`excluders` must be defined on axes that are given by consecutive
generators. Generators with axes filtered by an excluder must also have a
common ``alternate_direction`` setting. An exception is made for the outermost
generator as it is not repeated.

The following is `not` legal::

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
    Excluder, CircularROI

    xs = LineGenerator("x", "mm", 0, 1, 2)
    ys = LineGenerator("y", "mm", 0, 1, 2)
    zs = LineGenerator("z", "mm", 0, 1, 2)
    exc = Excluder(CircularROI([0, 0], 1), ["x", "z"])
    gen = CompoundGenerator([zs, ys, xs], [exc], []) # xs and zs are not consecutive
