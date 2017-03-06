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

The initializer performs some basic validation on the parameters and stores
them. The units get stored as a dictionary attribute of axis->unit:

.. literalinclude:: ../scanpointgenerator/generators/linegenerator.py
    :pyobject: LineGenerator.prepare_arrays

This is used by CompoundGenerator to create the points for this generator.
This method should create, for each axis the generator defines, an array of
positions by transforming the input index array.
The index array will be the numpy array [0, 1, 2, ..., n-1, n] for normal
positions, and [-0.5, 0.5, 1.5, ..., n-0.5, n+0.5] when used to calculate
boundary positions.

The arrays are returned as a dictionary of {axis_name : numpy float array}
