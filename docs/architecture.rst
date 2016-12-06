Architecture
============

Scan points are produced by a :ref:`compoundgenerator` that wraps base generators,
:ref:`excluders` and :ref:`mutators`.

All Generators inherit from the Generator baseclass, which provides the
following API:

.. module:: scanpointgenerator

.. autoclass:: Generator
    :members:

Each point produced by the iterator represents a scan point, with the following
API:

.. autoclass:: Point
    :members:

Using the API
-------------

A basic use case that uses two generators looks like this::

    cgen = CompoundGenerator([outer_generator, inner_generator], [], [])
    cgen.prepare()
    for point in cgen.iterator():
        for mname, mpos in point.positions():
            motors[mname].move(mpos)
        det.write_data_to_index(point.indexes)
