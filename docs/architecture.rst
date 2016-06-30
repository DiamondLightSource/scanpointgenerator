Architecture
============

Every scan point generator inherits from the ScanPointGenerator baseclass. This
baseclass provides the following API:

.. module:: scanpointgenerator

.. autoclass:: Generator
    :members:

Each point produced by the iterator represents a scan point, with the following
API:

.. autoclass:: Point
    :members:

Using the API
-------------

You would use a generator in a step scan like this::

    >>> for point in generator.iterator():
    >>>     for mname, mpos in point.positions():
    >>>         motors[mname].move(mpos)
    >>>     det.write_data_to_index(point.indexes)




