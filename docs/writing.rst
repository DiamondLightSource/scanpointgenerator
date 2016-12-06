Writing new scan point generators
=================================

.. module:: scanpointgenerator

Let's walk through the simplest generator, :class:`LineGenerator`, and see how
it is written.

.. literalinclude:: ../scanpointgenerator/generators/linegenerator.py
    :lines: 1-2

We import the baseclass :class:`Generator` and the compatibility wrappers
around the Python :py:func:`range` function and the :py:mod:`numpy` module

.. literalinclude:: ../scanpointgenerator/generators/linegenerator.py
    :lines: 12-14

Our new subclass includes a docstring giving a short explanation of what it does
and registers itself as a subclass of Generator for deserialization purposes.

.. literalinclude:: ../scanpointgenerator/generators/linegenerator.py
    :pyobject: LineGenerator.__init__

The initialiser stores the arguments given to it, then generates the three
properties that are required by the baseclass:

- position_units: Dict of str position_name -> str position_unit
- index_dims: List of int dimension sizes for the dataset
- index_names: List of str dimension names for the dataset

It is important to note that the position_units property will have the same
number of elements as index_dims for grid based scans (like LineGenerator). For
non grid based scans (like SpiralGenerator), index_dims will typically have
less elements, because the last two or more dimensions will be unrolled into
one long array. This avoids sparse datasets.

.. literalinclude:: ../scanpointgenerator/generators/linegenerator.py
    :pyobject: LineGenerator.produce_points

This is used by CompoundGenerator to create the points for this generator.
In here, we should create an array of points for each axis and store them in
a dictionary attribute, using the axis names for the key. The same should be
done for the boundaries between points.

The dictionaries are {axis_name : numpy float array}:

- self.points: The capture positions corresponding to the centre of
  the scan frame
- self.bounds: The boundary between points for continuous scanning.

As a rule, if the position of points can be parameterised by
``[f(t) for t in range(num_points)]`` then the bounds should be given by
``[f(t - 0.5) for t in range(num_points + 1)]``
