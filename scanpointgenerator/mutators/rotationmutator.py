###
# Copyright (c) 2019 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Bryan Tester
#
###

from annotypes import Anno, Union, Array, Sequence
from math import cos, sin, pi
from scanpointgenerator.core import Mutator, Point

with Anno("Axes to apply rotation to, "
          "in the order the offsets should be applied"):
    AAxes = Array[str]
UAxes = Union[AAxes, Sequence[str], str]
with Anno("Centre of rotation"):
    ACoR = Array[float]
UCoR = Union[ACoR, Sequence[float]]
with Anno("Angle by which to rotate points (in degrees)"):
    ARotationAngle = float


@Mutator.register_subclass("scanpointgenerator:mutator/RotationMutator:1.0")
class RotationMutator(Mutator):
    """Mutator to apply a rotation to the points of an ND
    ScanPointGenerator"""

    def __init__(self, axes, angle, centreOfRotation):
        # type: (UAxes, ARotationAngle, UCoR) -> None
        self.angle = ARotationAngle(angle)
        self.axes = AAxes(axes)
        self.centreOfRotation = ACoR(centreOfRotation)
        msg = "Can only rotate in the plane of a pair of orthogonal axes"
        assert len(self.axes) == 2, msg
        assert len(self.centreOfRotation) == 2, msg

    def mutate(self, point, idx):
        rotated = Point()
        rotated.indexes = point.indexes
        rotated.lower = point.lower.copy()
        rotated.upper = point.upper.copy()
        rotated.duration = point.duration
        pos = point.positions
        rotated.positions = pos.copy()
        i = self.axes[0]
        j = self.axes[1]
        i_off = self.centreOfRotation[0]
        j_off = self.centreOfRotation[1]
        rad = pi*(self.angle/180.0)  # convert degrees to radians
        rotated.positions[i] = (cos(rad) * (pos[i] - i_off)
                                - sin(rad) * (pos[j] - j_off)) + i_off
        rotated.positions[j] = (cos(rad) * (pos[j] - j_off)
                                + sin(rad) * (pos[i] - i_off)) + j_off
        if (i in point.lower and i in point.upper)\
                or (j in point.lower and j in point.upper):
            i_low = pos[i]
            i_up = pos[i]
            j_up = pos[j]
            j_low = pos[j]
            if j in point.lower:
                j_low = point.lower[j]
            if j in point.upper:
                j_up = point.upper[j]
            if i in point.lower:
                i_low = point.lower[i]
            if i in point.upper:
                i_up = point.upper[i]
            rotated.upper[i] = (cos(rad) * (i_up - i_off) - sin(rad) * (j_up - j_off)) + i_off
            rotated.upper[j] = (cos(rad) * (j_up - j_off) + sin(rad) * (i_up - i_off)) + j_off
            rotated.lower[i] = (cos(rad) * (i_low - i_off) - sin(rad) * (j_low - j_off)) + i_off
            rotated.lower[j] = (cos(rad) * (j_low - j_off) + sin(rad) * (i_low - i_off)) + j_off
        return rotated
