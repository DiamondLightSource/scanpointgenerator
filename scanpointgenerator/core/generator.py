###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Serializable, Anno, Array, Sequence, Union, TYPE_CHECKING

from scanpointgenerator.compat import np

if TYPE_CHECKING:
    from typing import Dict


with Anno("List of scannable names contributed to each Point"):
    AAxes = Array[str]
UAxes = Union[AAxes, Sequence[str], str]
with Anno("The units that the scannables are demanded in"):
    AUnits = Array[str]
UUnits = Union[AUnits, Sequence[str], str]
with Anno("The number of Points that this generator will produce"):
    ASize = int
with Anno("Whether to reverse on each alternate run of the generator"):
    AAlternate = bool


class Generator(Serializable):
    """Base class for all malcolm scan point generators"""

    def __init__(self, axes, units, size, alternate=False):
        # type: (UAxes, UUnits, ASize, AAlternate) -> None
        self.axes = AAxes(axes)
        assert len(self.axes) == len(set(self.axes)), \
            "Axis names cannot be duplicated; given %s" % list(self.axes)
        self.units = AUnits(units)
        # If only one set of units given, use those for all axes
        if len(self.units) == 1:
            self.units = AUnits(self.units.seq * len(self.axes))
        assert len(self.axes) == len(self.units), \
            "Units array %s length != axes array %s length" % (
                list(self.units), list(self.axes))
        self.size = ASize(size)
        assert self.size > 0, "Expected size > 0, got size = %d" % self.size
        self.alternate = AAlternate(alternate)
        # These will be filled in by prepare_*
        self.positions = None
        self.bounds = None

    def axis_units(self):
        # type: () -> Dict[str, float]
        """Return the units for each axis in a dict"""
        return dict(zip(self.axes, self.units))

    def prepare_arrays(self, index_array):
        # type: (np.array) -> Dict[str, np.array]
        """
        Abstract method to create position or bounds array from provided index
        array. index_array will be np.arange(self.size) for positions and
        np.arange(self.size + 1) - 0.5 for bounds.

        Args:
            index_array (np.array): Index array to produce parameterised points

        Returns:
            Positions: Dictionary of axis names to position/bounds arrays
        """
        raise NotImplementedError

    def prepare_positions(self):
        self.positions = self.prepare_arrays(np.arange(self.size))

    def prepare_bounds(self):
        self.bounds = self.prepare_arrays(np.arange(self.size + 1) - 0.5)
