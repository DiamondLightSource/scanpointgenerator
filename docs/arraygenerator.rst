Array Generator
===============

.. module:: scanpointgenerator

.. autoclass:: ArrayGenerator
    :members:

Examples
--------

This example defines a motor "x" with units "mm" which is being scanned
over the series of positions [0, 1, 1.5, 1.8, 2, 2.1, 2.25, 3]

.. plot::
    :include-source:

    from scanpointgenerator import ArrayGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    positions = [0, 1, 1.5, 1.8, 2, 2.1, 2.25, 3]
    gen = ArrayGenerator("x", "mm", positions)
    plot_generator(gen)
