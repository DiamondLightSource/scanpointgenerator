Static Point Generator
====================

.. module:: scanpointgenerator

.. autoclass:: StaticPointGenerator
    :members:

Examples
--------

Produce empty points to "multiply" existing generators within a :ref:`compoundgenerator`, adding an extra dimension.

    >>> from scanpointgenerator import StaticPointGenerator, LineGenerator, CompoundGenerator
    >>> line_gen = LineGenerator("x", "mm", 0.0, 1.0, 3)
    >>> nullpoint_gen = StaticPointGenerator(2)
    >>> gen = CompoundGenerator([nullpoint_gen, line_gen], [], [])
    >>> gen.prepare()
    >>> [point.positions for point in gen.iterator()]
    [{'x': 0.0}, {'x': 0.5}, {'x': 1.0}, {'x': 0.0}, {'x': 0.5}, {'x': 1.0}]


Using a StaticPointGenerator on its own in a compound generator is also allowed.

    >>> from scanpointgenerator import StaticPointGenerator, CompoundGenerator
    >>> nullpoint_gen = StaticPointGenerator(3)
    >>> gen = CompoundGenerator([nullpoint_gen], [], [])
    >>> gen.prepare()
    >>> [point.positions for point in gen.iterator()]
    [{}, {}, {}]
