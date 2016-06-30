Lissajous Generator
===================

.. module:: scanpointgenerator

.. autoclass:: LissajousGenerator
    :members:

Examples
--------

This example defines motors "x" and "y" with engineering units "mm" which
will be scanned over a 3x4 lobe Lissajous curve with filling a 1x1mm rectangle.

.. plot::
    :include-source:

    from scanpointgenerator import LissajousGenerator, plot_generator

    box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    gen = LissajousGenerator(['x', 'y'], "mm", box=box, num_lobes=3, num_points=50)
    plot_generator(gen)

The number of points has been lowered from the default to make the plot visible.
The following plot is for 10x11 lobes with the default number of points.

.. plot::
    :include-source:

    from scanpointgenerator import LissajousGenerator, plot_generator

    box = dict(centre=[0.0, 0.0], width=1.0, height=1.0)
    gen = LissajousGenerator(['x', 'y'], "mm", box=box, num_lobes=10)
    plot_generator(gen)