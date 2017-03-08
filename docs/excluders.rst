.. _excluders:

Excluders
=========

Excluders are used to filter points in a generator based on a pair of
coordinates and some attribute of the point, for example its position or
duration.

ROIExcluders
============

ROIExcluders filter points that fall outside of a given a region of interest.

.. module:: scanpointgenerator

.. autoclass:: ROIExcluder
    :members:

CircularROI Example
-------------------

Here we use CircularROIs to filter the points of a snake scan

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
    ROIExcluder, CircularROI
    from scanpointgenerator.plotgenerator import plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circles = ROIExcluder([CircularROI([1.0, 2.0], 2.0),
                           CircularROI([2.0, 1.0], 2.0)], ["x", "y"])
    gen = CompoundGenerator([y, x], [], [])
    plot_generator(gen, circles)

And with the excluder applied

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
    ROIExcluder, CircularROI
    from scanpointgenerator.plotgenerator import plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    circles = ROIExcluder([CircularROI([1.0, 2.0], 2.0),
                           CircularROI([2.0, 1.0], 2.0)], ["x", "y"])
    gen = CompoundGenerator([y, x], [circles], [])
    plot_generator(gen, circle)
