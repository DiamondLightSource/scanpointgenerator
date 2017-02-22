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
    :pyobject: LineGenerator.prepare_arrays

This is used by CompoundGenerator to create the points for this generator.
This method should create, for each axis the generator defines, an array of
positions by transforming the input index array.
The index array will be the numpy array [0, 1, 2, ..., n-1, n] for normal
positions, and [-0.5, 0.5, 1.5, ..., n-0.5, n+0.5] when used to calculate
boundary positions.

The arrays are returned as a dictionary of {axis_name : numpy float array}
