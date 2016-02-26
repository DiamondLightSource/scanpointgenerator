Architecture
============

Every scan point generator inherits from the ScanPointGenerator baseclass. This
baseclass provides the following API:

.. module:: scanpointgenerator

.. autoclass:: ScanPointGenerator
    :members:

Each point produced by the iterator represents a scan point, with the following
API:

.. autoclass:: Point
    :members:

Using the API
-------------

You call the thing like this::

    >>> for point in generator.positions():
    >>>     for mname, mpos in point.positions.items():
    >>>         motors[mname].move(mpos)
    >>>     det.write_data_to_index(point.indexes)




