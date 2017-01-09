.. _mutators:

Mutators
========

Mutators are used for post processing points after they have been generated
and filtered by any regions of interest.

.. module:: scanpointgenerator

.. autoclass:: Mutator
    :members:

RandomOffsetMutator
-------------------

This is used to apply a random offset to each point in an iterator. Here we
apply it to a snake scan

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate_direction=True)
    ys = LineGenerator("y", "mm", 0.0, 0.5, 4)
    gen = CompoundGenerator([ys, xs], [], [])
    plot_generator(gen)

And with the random offset

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, RandomOffsetMutator
    from scanpointgenerator.plotgenerator import plot_generator

    xs = LineGenerator("x", "mm", 0.0, 0.5, 5, alternate_direction=True)
    ys = LineGenerator("y", "mm", 0.0, 0.5, 4)
    random_offset = RandomOffsetMutator(seed=12345, axes = ["x", "y"], max_offset=dict(x=0.05, y=0.05))
    gen = CompoundGenerator([ys, xs], [], [random_offset])
    plot_generator(gen)


Example with a spiral

.. plot::
    :include-source:

    from scanpointgenerator import SpiralGenerator, CompoundGenerator, RandomOffsetMutator
    from scanpointgenerator.plotgenerator import plot_generator

    spiral = SpiralGenerator(["x", "y"], ["mm", "mm"], [0., 0.], 5.0, 1.25)
    random_offset = RandomOffsetMutator(seed=12345, axes = ["x", "y"], max_offset=dict(x=0.2, y=0.2))
    gen = CompoundGenerator([spiral], [], [random_offset])
    plot_generator(gen)
