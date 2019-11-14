Change Log
==========
All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

`Unreleased`_
-------------

`3-0`_ - 2019-11-14
-------------------

Added:

- ZipGenerator
- ConcatGenerator
- delay_after argument to CompoundGenerator

Changed:

- LineGenerator single points case puts point in centre of start/stop
- Licence changed back to Apache License 2.0
- excluders and mutator arguments to CompoundGenerator default to []
- Dimensions may contain alternating and non-alternating generators, but in some
  complex cases this may change the order that generators are executed. See #68


`2-3`_ - 2019-08-09
-------------------

Added:

- New get_mesh_map function to Dimension class to get mesh indices
- Squashing Excluder

Changed:

- Made ArrayGenerator backwards compatible by handling 'axis' init argument
- RandomOffsetMutator to take array of floats instead of dict for max offset arg
- StaticPointGenerator to take an optional axes argument for a single axis
- Gave CompoundGenerator mutators and excluders defaults of ()
- Now requires typing module

Fixed:

- Various annotypes fixes

`2-2-1`_ - 2019-03-28
---------------------

Fixed:

- DLS specific build changes for setuptools multi-version

`2-2`_ - 2019-03-21
-------------------

Changed:

- Converted Generators, Excluders, Mutators, and ROIS to use annotypes
- Removed python 3.3 and 3.4 from travis build, and added 3.6
- Updated to annotypes 0.13 to bring in sphinx extension for documentation

`2-1-1`_ - 2018-04-30
---------------------

Added:

- Tags now cause Travis to deploy to PyPi
- Added StaticPointGenerator
- Allow ROI to span multiple Dimensions
- Add continuous property to CompoundGenerator

Fixed:

- Fixed plotgenerator to interpolate turnarounds properly 

`2-1-0`_ - 2017-04-18
---------------------

Fixed:

- Fixed incorrect comparison PolygonalROI mask_points that resulted in an incorrect mask
- Point bounds are now giben for a grid scan in a rectangular region

Changed:

- Use numpy import when running in Jython instead of "numjy"

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

.. _Unreleased: https://github.com/dls-controls/scanpointgenerator/compare/3-0...HEAD
.. _3-0: https://github.com/dls-controls/scanpointgenerator/compare/2-3..3-0
.. _2-3: https://github.com/dls-controls/scanpointgenerator/compare/2-2-1...2-3
.. _2-2-1: https://github.com/dls-controls/scanpointgenerator/compare/2-2...2-2-1
.. _2-2: https://github.com/dls-controls/scanpointgenerator/compare/2-1-1...2-2
.. _2-1-1: https://github.com/dls-controls/scanpointgenerator/compare/2-1-0...2-1-1
.. _2-1-0: https://github.com/dls-controls/scanpointgenerator/compare/2-0-0...2-1-0
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

