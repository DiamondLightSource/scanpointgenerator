Concat Generator
================

.. module:: scanpointgenerator

.. autoclass:: ConcatGenerator
    :members:

Examples
--------

This example takes two generators as inputs and merges them together, so that
the points from gen_two and places after the points from gen_one in the final
generator output

.. plot::
    :include-source:

    from scanpointgenerator import ConcatGenerator, LineGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    gen_one = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.], [4., -4.], 3)
    gen_two = LineGenerator(["x", "y"], ["mm", "mm"], [5., -4.], [7., -2.], 3)
    gen = ConcatGenerator([gen_one, gen_two])
    plot_generator(gen)

