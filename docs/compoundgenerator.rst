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

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate=False)
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

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate=True)
    ys = LineGenerator("y", "mm", 0.0, 0.5, 4)
    gen = CompoundGenerator([ys, xs], [], [])
    plot_generator(gen)


.. _compoundgenerator_restrictions:

Restrictions
------------

Generators with axes filtered by an excluder or between any such generators
must have a common ``alternate`` setting. An exception is made for the
outermost generator as it is not repeated.
