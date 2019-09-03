###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Serializable, Anno, Array, Union, Sequence

from scanpointgenerator.compat import np

with Anno("Names of axes to exclude points from"):
    AExcluderAxes = Array[str]
UExcluderAxes = Union[AExcluderAxes, Sequence[str], str]


class Excluder(Serializable):

    """Base class for objects that filter points based on their attributes."""

    def __init__(self, axes):
        # type: (UExcluderAxes) -> None
        self.axes = AExcluderAxes(axes)

    def create_mask(self, *point_arrays):
        # type: (np.array) -> np.array
        raise NotImplementedError("Method must be implemented in child class.")
