Power Term Generator
====================

.. module:: scanpointgenerator

.. autoclass:: PowerTermGenerator
    :members:

This generator will produce points with high density around a focus point, getting coarser as the distance from the
focus increases.

Examples
--------

Generate points from 250 to 360 according to a cubic term centred around 280.

.. plot::
    :include-source:

    from scanpointgenerator import PowerTermGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    gen = PowerTermGenerator("x", "eV", 250, 360, 280, 3, 5)
    plot_generator(gen)
