###
# Copyright (c) 2016, 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
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
