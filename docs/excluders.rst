Excluders
=========

Excluders are used to filter points in a generator based on a pair of
coordinates and a region of interest.

.. module:: scanpointgenerator

.. autoclass:: Excluder
    :members:

CircularROI Example
-------------------

Here we use a CircularROI to filter the points of a snake scan

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, plot_generator
    from scanpointgenerator.circular_roi import CircularROI

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circle = CircularROI([2.0, 1.0], 2.0)
    gen = CompoundGenerator([x, y], [], [])
    plot_generator(gen, circle)

And with the excluder applied

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, Excluder, plot_generator
    from scanpointgenerator.circular_roi import CircularROI

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circle = CircularROI([2.0, 1.0], 2.0)
    excluder = Excluder(circle, ['x', 'y'])
    gen = CompoundGenerator([x, y], [excluder], [])
    plot_generator(gen, circle)