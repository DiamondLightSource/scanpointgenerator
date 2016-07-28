Spiral Generator
================

.. module:: scanpointgenerator

.. autoclass:: SpiralGenerator
    :members:

Examples
--------

This example defines motors "x" and "y" with engineering units "mm" which
will be scanned in a spiral filling a circle of radius 5mm.

.. plot::
    :include-source:

    from scanpointgenerator import SpiralGenerator, plot_generator

    gen = SpiralGenerator("XYSpiral", "mm", [0.0, 0.0], 5.0)
    plot_generator(gen)

In this example the spiral is scaled to be more sparse.

.. plot::
    :include-source:

    from scanpointgenerator import SpiralGenerator, plot_generator

    gen = SpiralGenerator("XYSpiral", "mm", [0.0, 0.0], 5.0, scale=2.0)
    plot_generator(gen)