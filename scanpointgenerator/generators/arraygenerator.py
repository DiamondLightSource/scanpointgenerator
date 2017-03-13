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

from scanpointgenerator.compat import np
from scanpointgenerator.core import Generator


@Generator.register_subclass("scanpointgenerator:generator/ArrayGenerator:1.0")
class ArrayGenerator(Generator):
    """Generate points fron a given list of positions"""

    def __init__(self, axis, units, points, alternate=False):
        """
        Args:
            axis (str): The scannable axis name
            units (str): The scannable units.
            points (list(double)): array positions
            alternate (bool): Alternate directions
        """

        self.alternate = alternate
        self.points = np.array(points, dtype=np.float64)
        self.size = len(self.points)
        self.axes = [axis]
        self.units = {axis:units}

    def prepare_arrays(self, index_array):
        points = self.points
        # add linear extension to ends of points, representing t=-1 and t=N+1
        v_left = points[0] - (points[1] - points[0])
        v_right = points[-1] + (points[-1] - points[-2])
        shape = points.shape
        shape = (shape[0] + 2,) + shape[1:]
        extended = np.empty(shape, dtype=points.dtype)
        extended[1:-1] = points
        extended[0] = v_left
        extended[-1] = v_right
        points = extended
        index_floor = np.floor(index_array).astype(np.int32)
        epsilon = index_array - index_floor
        index_floor += 1
        values = points[index_floor] + epsilon * (points[index_floor+1] - points[index_floor])
        return {self.axes[0]:values}

    def to_dict(self):
        """Serialize ArrayGenerator to dictionary"""

        d = {
                "typeid":self.typeid,
                "axis":self.axes[0],
                "units":self.units[self.axes[0]],
                "points":self.points.tolist(),
                "alternate":self.alternate,
            }
        return d

    @classmethod
    def from_dict(cls, d):
        """
        Create a ArrayGenerator from serialized form.

        Args:
            d (dict): Serialized generator

        Returns:
            ArrayGenerator: New ArrayGenerator instance
        """

        axis = d["axis"]
        units = d["units"]
        alternate = d["alternate"]
        points = d["points"]
        return cls(axis, units, points, alternate)
