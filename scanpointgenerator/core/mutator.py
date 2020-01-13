###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Serializable, Union, Array
from scanpointgenerator.core import Point, Points

UPoint = Union[Point, Points]
UInt = Union[int, Array[int]]

class Mutator(Serializable):
    """Abstract class to apply a mutation to point/points of an ND
     ScanPointGenerator"""

    def mutate(self, point, index):
        # type: (UPoint, Uint) -> UPoint
        """
        Abstract method to take a Point or Points, apply a mutation and then return the
        new point

        Args:
            point: Point or Points object to mutate
            index: ind[ex/ices] of the Point[s] to mutate

        Returns:
            Point: Mutated point
        """
        raise NotImplementedError
