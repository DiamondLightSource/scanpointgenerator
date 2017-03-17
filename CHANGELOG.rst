Change Log
==========
All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Unreleased
----------

Added:

- Nothing yet

`2-0-0`_ - 2017-03-17
---------------------

Added:

- Adds dependency on numpy
- Added Dimension class, providing points along a dataset dimension
- Add dimensions attribute to CompoundGenerator
- Add shape attribute to CompoundGenerator
- Jython builds using a numpy emulator are tested
- Add ROIExcluder, replacing previous use of Excluder (now a generic base class)

Changed:

- Rewrite Generator mechanisms to use vectorised operations for point calculation
- Generators now only usable through CompoundGenerator
- CompoundGenerator requires call to prepare before use
- CompoundGenerator now takes a duration argument, replacing FixedDurationMutator (removed)
- Rename name/names to axes in Generators
- Rename scannables to axes in Excluders
- Generators take an array for units with the same size as axes
- Rename num_points to size and num_lobes to lobes in LissajousGenerator
- PolygonalROI takes separate x,y arrays for its vertices
- Bounds are only applied to the innermost axis/axes
- Remove index_names and index_dims from Generators
- License changed to Eclipse Public License v1.0

`1-6-1`_ - 2016-10-27
---------------------

Fixed:

- Add workaround for GDA not working with threading

`1-6`_ - 2016-10-18
-------------------

Fixed:

- CompoundGenerator to set the right number of points if excluders are used

Changed:

- Refactored internal structure of modules

`1-5`_ - 2016-10-07
-------------------

Added:

- Add full ROI set and FixedDurationMutator

`1-4`_ - 2016-09-22
-------------------

Added:

- Caching of points to CompoundGenerator

`1-3-1`_ - 2016-09-13
---------------------

Added:

- Serialisation for ROIs
- Change type to typeid to match with Malcolm

`1-3`_ - 2016-08-31
-------------------
Added:

- Remove OrderedDict entirely for 2.5 back-compatibility

Changed:

- type is now typeid to make it compatible with malcolm

`1-2-1`_ - 2016-08-17
---------------------
Fixed:

- Refactor RandomOffsetMutator to be consistent in Jython and Python without OrderedDict in Point

`1-2`_ - 2016-08-17
-------------------
Added:

- Remove OrderedDict from Point and speed up LineGenerator

`1-1`_ - 2016-08-16
-------------------
Added:

- Small tweaks for GDA and script to push changes to daq-eclipse on release

`1-0`_ - 2016-07-18
-------------------
Added:

- Initial requirements for GDA and Malcolm

`0-5`_ - 2016-06-20
-------------------
Added:

- Additions to work with GDA and Malcolm

`0-4`_ - 2016-04-15
-------------------
Added:

- MANIFEST.in file to allow install in travis builds

`0-3`_ - 2016-03-03
-------------------
Added:

- Documentation on writing new generators

`0-2`_ - 2016-02-29
-------------------
Added:

- Documentation
- Indexes to plots

0-1 - 2016-02-26
----------------
Added:

- Initial structure with Line and Nested generators

.. _2-0-0: https://github.com/dls-controls/scanpointgenerator/compare/1-6-1...2-0-0
.. _1-6-1: https://github.com/dls-controls/scanpointgenerator/compare/1-6...1-6-1
.. _1-6: https://github.com/dls-controls/scanpointgenerator/compare/1-5...1-6
.. _1-5: https://github.com/dls-controls/scanpointgenerator/compare/1-4...1-5
.. _1-4: https://github.com/dls-controls/scanpointgenerator/compare/1-3-1...1-4
.. _1-3-1: https://github.com/dls-controls/scanpointgenerator/compare/1-3...1-3-1
.. _1-3: https://github.com/dls-controls/scanpointgenerator/compare/1-2-1...1-3
.. _1-2-1: https://github.com/dls-controls/scanpointgenerator/compare/1-2...1-2
.. _1-2: https://github.com/dls-controls/scanpointgenerator/compare/1-1...1-2
.. _1-1: https://github.com/dls-controls/scanpointgenerator/compare/1-0...1-1
.. _1-0: https://github.com/dls-controls/scanpointgenerator/compare/0-5...1-0
.. _0-5: https://github.com/dls-controls/scanpointgenerator/compare/0-4...0-5
.. _0-4: https://github.com/dls-controls/scanpointgenerator/compare/0-3...0-4
.. _0-3: https://github.com/dls-controls/scanpointgenerator/compare/0-2...0-3
.. _0-2: https://github.com/dls-controls/scanpointgenerator/compare/0-1...0-2

