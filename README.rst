Scan Point Generator
====================

|build-status| |coverage| |health| |pypi-version| |readthedocs|

Scan point generator contains a number of python iterators that are used in
`GDA`_ and `malcolm`_ to determine the motor demand positions and dataset
indexes that various scan types will produce

Installation
------------
To install the latest release, type::

    pip install scanpointgenerator

To install the latest code directly from source, type::

    pip install git+git://github.com/dls-controls/scanpointgenerator.git

Changelog
---------

See `CHANGELOG`_

Contributing
------------

See `CONTRIBUTING`_

License
-------
APACHE License. (see `LICENSE`_)

Documentation
-------------

Full documentation is available at http://scanpointgenerator.readthedocs.org

.. |build-status| image:: https://travis-ci.org/dls-controls/scanpointgenerator.svg?style=flat
    :target: https://travis-ci.org/dls-controls/scanpointgenerator
    :alt: Build Status

.. |coverage| image:: https://coveralls.io/repos/dls-controls/scanpointgenerator/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/dls-controls/scanpointgenerator?branch=master
    :alt: Test coverage

.. |pypi-version| image:: https://img.shields.io/pypi/v/scanpointgenerator.svg
    :target: https://pypi.python.org/pypi/scanpointgenerator/
    :alt: Latest PyPI version

.. |readthedocs| image:: https://readthedocs.org/projects/scanpointgenerator/badge/?version=latest
    :target: http://scanpointgenerator.readthedocs.org
    :alt: Documentation

.. |health| image:: https://landscape.io/github/dls-controls/scanpointgenerator/master/landscape.svg?style=flat
   :target: https://landscape.io/github/dls-controls/scanpointgenerator/master
   :alt: Code Health

.. _CHANGELOG: https://github.com/dls-controls/scanpointgenerator/blob/master/CHANGELOG.rst
.. _CONTRIBUTING: https://github.com/dls-controls/scanpointgenerator/blob/master/CONTRIBUTING.rst
.. _LICENSE: https://github.com/dls-controls/scanpointgenerator/blob/master/LICENSE
.. _GDA: http://www.opengda.org/
.. _malcolm: https://github.com/dls-controls/malcolm
