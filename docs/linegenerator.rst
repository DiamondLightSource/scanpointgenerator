Line Generator
==============

.. module:: scanpointgenerator

.. autoclass:: LineGenerator
    :members:

Examples
--------

This example defines a motor "x" with engineering units "mm" which is being
scanned from 0mm to 1mm with 5 scan points inclusive of the start.
Note that the capture points are as given, so the bounds will be +-0.5*step
of each capture point.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    gen = LineGenerator("x", "mm", 0.0, 1.0, 5)
    plot_generator(gen)

LineGenerator is N dimensional; just pass in ND lists for name, start and stop.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    gen = LineGenerator(["x", "y"], "mm", [1.0, 2.0], [5.0, 10.0], 5)
    plot_generator(gen)
