Zip Generator
==============

.. module:: scanpointgenerator

.. autoclass:: ZipGenerator
    :members:

Examples
--------

This example defines two LineGenerators and combines them together, effectively
creating a single two-dimensional generator. The source generators must be of
the same size and can't have overlapping axes.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, ZipGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
    gentwo = LineGenerator("y", "mm", 11, 19, 5)
    gen = ZipGenerator([genone, gentwo])

    plot_generator(gen)

