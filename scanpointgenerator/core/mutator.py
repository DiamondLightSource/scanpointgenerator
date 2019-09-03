###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Serializable

from scanpointgenerator.core import Point


class Mutator(Serializable):
    """Abstract class to apply a mutation to the points of an ND
     ScanPointGenerator"""

    def mutate(self, point, index):
        # type: (Point, int) -> Point
        """
        Abstract method to take a point, apply a mutation and then return the
        new point

        Args:
            point: point to mutate
            index: one-dimensional linear index of point

        Returns:
            Point: Mutated point
        """
        raise NotImplementedError
