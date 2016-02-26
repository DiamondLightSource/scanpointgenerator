Line Generator
==============

Things and plots

.. module:: scanpointgenerator

.. autoclass:: LineGenerator
    :members:

Examples
--------

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, plot_generator

    gen = LineGenerator("x", "mm", 0, 0.1, 5)
    plot_generator(gen)
