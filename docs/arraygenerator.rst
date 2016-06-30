Array Generator
===============

.. module:: scanpointgenerator

.. autoclass:: ArrayGenerator
    :members:

Examples
--------

The ArrayGenerator takes an N-Dimensional array of coordinates and creates
Points with calculated upper and lower bounds. You can also provide your
own bounds.

.. plot::
    :include-source:

    from scanpointgenerator import ArrayGenerator, plot_generator

    points = [[0.0], [2.0], [3.0], [5.0], [7.0], [8.0]]
    array = ArrayGenerator(["x"], "mm", points)
    plot_generator(array)

And a 2D scan.

.. plot::
    :include-source:

    from scanpointgenerator import ArrayGenerator, plot_generator

    points = [[0.0, 2.0], [2.0, 3.0], [3.0, 5.0], [5.0, 6.0], [7.0, 7.0], [8.0, 9.0]]
    array = ArrayGenerator(["x", "y"], "mm", points)
    plot_generator(array)