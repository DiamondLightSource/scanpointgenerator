Line Generator
==============

.. module:: scanpointgenerator

.. autoclass:: LineGenerator
    :members:

Examples
--------

This example defines a motor "x" with engineering units "mm" which is being
scanned from a start of 0mm, with a step of 0.1mm, and 5 scan points inclusive
of the start. Note that the capture points are as given, so the bounds will
be +-0.5*step of each capture point.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, plot_generator

    gen = LineGenerator("x", "mm", 0, 0.1, 5)
    plot_generator(gen)
