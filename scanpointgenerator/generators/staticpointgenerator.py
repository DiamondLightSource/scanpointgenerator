###
# Copyright (c) 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

import numpy as np
from scanpointgenerator.core import Generator, ASize, UAxes, AAxes


@Generator.register_subclass(
    "scanpointgenerator:generator/StaticPointGenerator:1.0")
class StaticPointGenerator(Generator):
    """Generate 'empty' points with optional axis information"""
    def __init__(self, size, axes=[]):
        # type: (ASize, UAxes) -> None

        axis = AAxes(axes)
        # Validate
        assert len(axis) <= 1, \
            "Expected 1D or no axes, got axes %s" % (
                list(axis))

        super(StaticPointGenerator, self).__init__(axes=axis,
                                                   units=[""] * len(axis),
                                                   size=size)

    def prepare_arrays(self, index_array):
        arrays = {}
        # If there is an axis in self.axes, produce a 1-indexed array for it
        for axis in self.axes:
            arrays[axis] = np.arange(1, len(index_array)+1)
        return arrays


