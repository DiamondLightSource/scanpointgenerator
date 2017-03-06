Creating a Generator
====================

The idea of CompoundGenerator is that you can combine generators, excluders
and mutators arbitrarily. The following will show some more extensive examples
to show the capabilities of scanpointgenerator. Remember to account for the
restrictions specified in :ref:`compoundgenerator_restrictions`.


A spiral scan with an offset rectangular roi overlay and randomly offset
points in the y direction

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, SpiralGenerator, \
    CompoundGenerator, Excluder, RandomOffsetMutator, RectangularROI
    from scanpointgenerator.plotgenerator import plot_generator

    spiral = SpiralGenerator(["x", "y"], "mm", [0.0, 0.0], 10.0,
                             alternate=True)
    rectangle = Excluder(RectangularROI([1.0, 1.0], 8.0, 8.0), ["x", "y"])
    mutator = RandomOffsetMutator(2, ["x", "y"], dict(x=0.0, y=0.25))
    gen = CompoundGenerator([spiral], [rectangle], [mutator])

    plot_generator(gen, rectangle)

A spiral scan at each point of a line scan with alternating direction

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, SpiralGenerator, \
    CompoundGenerator

    line = LineGenerator("z", "mm", 0.0, 20.0, 3)
    spiral = SpiralGenerator(["x", "y"], "mm", [0.0, 0.0], 1.2,
                             alternate=True)
    gen = CompoundGenerator([line, spiral], [], [])
    gen.prepare()

    for point in gen.iterator():
        for axis, value in point.positions.items():
            point.positions[axis] = round(value, 3)
        print(point.positions)

::

    {'y': -0.321, 'x': 0.237, 'z': 0.0}
    {'y': -0.25, 'x': -0.644, 'z': 0.0}
    {'y': 0.695, 'x': -0.56, 'z': 0.0}
    {'y': 0.992, 'x': 0.361, 'z': 0.0}
    {'y': 0.992, 'x': 0.361, 'z': 10.0}
    {'y': 0.695, 'x': -0.56, 'z': 10.0}
    {'y': -0.25, 'x': -0.644, 'z': 10.0}
    {'y': -0.321, 'x': 0.237, 'z': 10.0}
    {'y': -0.321, 'x': 0.237, 'z': 20.0}
    {'y': -0.25, 'x': -0.644, 'z': 20.0}
    {'y': 0.695, 'x': -0.56, 'z': 20.0}
    {'y': 0.992, 'x': 0.361, 'z': 20.0}

Three nested line scans with an excluder operating on the two innermost axes

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
    Excluder, CircularROI

    line1 = LineGenerator("x", "mm", 0.0, 2.0, 3)
    line2 = LineGenerator("y", "mm", 0.0, 1.0, 2)
    line3 = LineGenerator("z", "mm", 0.0, 1.0, 2)
    circle = Excluder(CircularROI([1.0, 1.0], 1.0), ["x", "y"])
    gen = CompoundGenerator([line3, line2, line1], [circle], [])
    gen.prepare()

    for point in gen.iterator():
        print(point.positions)

::

    {'y': 0.0, 'x': 1.0, 'z': 0.0}
    {'y': 0.0, 'x': 1.0, 'z': 1.0}
    {'y': 1.0, 'x': 0.0, 'z': 0.0}
    {'y': 1.0, 'x': 1.0, 'z': 0.0}
    {'y': 1.0, 'x': 2.0, 'z': 0.0}
    {'y': 1.0, 'x': 0.0, 'z': 1.0}
    {'y': 1.0, 'x': 1.0, 'z': 1.0}
    {'y': 1.0, 'x': 2.0, 'z': 1.0}
