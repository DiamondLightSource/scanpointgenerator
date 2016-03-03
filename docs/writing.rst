Writing new scan point generators
=================================

.. module:: scanpointgenerator

Let's walk through the simplest generator, :class:`LineGenerator`, and see how
it is written.

.. literalinclude:: ../scanpointgenerator/linegenerator.py
    :lines: 1-2

We import the baseclass :class:`ScanPointGenerator` and the :class:`Point` class
that we will be generating instances of.

.. literalinclude:: ../scanpointgenerator/linegenerator.py
    :lines: 5-6

Our new subclass includes a docstring giving a short explanation of what it does

.. literalinclude:: ../scanpointgenerator/linegenerator.py
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

.. literalinclude:: ../scanpointgenerator/linegenerator.py
    :pyobject: LineGenerator._calc

We have a repeated bit of code here, so have pulled it out into a function. It
calculates the position of a point given an index

.. literalinclude:: ../scanpointgenerator/linegenerator.py
    :pyobject: LineGenerator.iterator

This is the entry point for external code. It is expecting us to produce a
number of :class:`Point` instances, one for each point in the scan. We are
required to fill in the following dictionaries of str position_name -> float
position:

- positions: The capture position corresponding to the centre of the scan frame
- lower: The lower bound of the scan frame if the scan is to be used for
  continuous scanning
- upper: The upper bound of the scan frame if the scan is to be used for
  continuous scanning

We also fill in the list of datapoint indexes:

- indexes: The index into the dataset that the data frame should be stored in

The `yield` keyword turns the python function into a generator, which can then
be used by the external program to iterate through points without evaluating
them all at the start.
