###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Joseph Ware - Points implementation
#
###

from scanpointgenerator.compat import np


class Point(object):
    """Contains information about for each scan point

    Attributes:
        positions (dict): Dict of str position_name -> float position for each
            scannable dimension. E.g. {"x": 1, "y": 2.2}
        lower (dict): Dict of str position_name -> float lower_bound for each
            scannable dimension. E.g. {"x": 0.95, "y": 2.15}
        upper (dict): Dict of str position_name -> float upper_bound for each
            scannable dimension. E.g. {"x": 1.05, "y": 2.25}
        indexes (list): List of int indexes for each dataset dimension, fastest
            changing last. E.g. [15]
        duration (int): Int or None for duration of the point exposure
        delay_after (float): Float or None. Insert a time delay after every point
    """
    def __init__(self):
        self.positions = {}
        self.lower = {}
        self.upper = {}
        self.indexes = []
        self.duration = None
        self.delay_after = None

    def __len__(self):
        return 1


class Points(object):
    """Contains information about multiple points

    Attributes:
        positions (dict): Dict of str position_name -> float array positions for each
            scannable dimension. E.g. {"x": [1, 1.1], "y": [2.2, 2.2]}
        lower (dict): Dict of str position_name -> float array lower_bounds for each
            scannable dimension. E.g. {"x": [0.95, 1.95]., "y": [2.1, 2.1]}
        upper (dict): Dict of str position_name -> float array upper_bounds for each
            scannable dimension. E.g. {"x": [1.05, 2.05], "y": [2.3, 2.3]}
        indexes (list): List of int array indexes for each dataset dimension, fastest
            changing last. E.g. [[16, 15], [16,16]]
        duration (int array): Int array or None for duration of the points exposures
        delay_after (float array): Float array or None. Insert a time delay after every point
    """
    def __init__(self):
        self.positions = {}
        self.lower = {}
        self.upper = {}
        self.indexes = []
        self.duration = None
        self.delay_after = None

    def __len__(self):
        return len(self.indexes)

    def __add__(self, other):
        """ input:
        other (Point or Points)
        Appends the positions, bounds, indices, duration, delay of another Points or Point to self
        Assumes that dimensions are shared, or that either self or other have no positions.
        returns: self
        """
        if not len(self):
            if isinstance(other, Points):
                return other.__copy__()
            return self.wrap(other)
        if len(other):
            self.positions.update({axis: np.append(self.positions[axis], other.positions[axis])
                                   for axis in other.positions})
            self.lower.update({axis: np.append(self.lower[axis], other.lower[axis]) for axis in other.lower})
            self.upper.update({axis: np.append(self.upper[axis], other.upper[axis]) for axis in other.upper})
            if isinstance(other, Point):
                self.indexes = np.vstack((self.indexes, other.indexes))
            elif len(other):
                self.indexes = np.concatenate((self.indexes, other.indexes), axis=0)
            self.duration = np.append(self.duration, other.duration)
            self.delay_after = np.append(self.delay_after, other.delay_after)
        return self

    def __getitem__(self, sliced):
        """
        input:
        sliced (int or slice)- index of a Point or a slice of many Point to consolidate into a Points
        returns: Point or Points object with each field reduced to the relevant indices
        """
        if isinstance(sliced, int):
            # Single position
            point = Point()
        else:
            point = Points()
        point.positions = {axis: self.positions[axis][sliced] for axis in self.positions}
        point.upper = {axis: self.upper[axis][sliced] for axis in self.upper}
        point.lower = {axis: self.lower[axis][sliced] for axis in self.lower}
        point.indexes = self.indexes[sliced]
        point.duration = self.duration[sliced]
        point.delay_after = self.delay_after[sliced]
        return point

    def extract(self, points):
        self.positions.update({axis: points.positions[axis].copy() for axis in points.positions})
        self.lower.update({axis: points.lower[axis].copy() for axis in points.lower})
        self.upper.update({axis: points.upper[axis].copy() for axis in points.upper})
        if len(self.indexes):  # if indices is not empty: assumption that length of indices is consistent
            self.indexes = np.column_stack((self.indexes, points.indexes))
        else:
            self.indexes = points.indexes

    def __copy__(self):
        points = Points()
        points.positions.update({self.positions[axis].copy() for axis in self.positions})
        points.lower.update({self.lower[axis].copy() for axis in self.lower})
        points.upper.update({self.upper[axis].copy() for axis in self.upper})
        points.delay_after = self.delay_after.copy()
        points.duration = self.duration.copy()
        points.indexes = self.indexes.copy()
        return points

    @staticmethod
    def wrap(point):
        """
        :param point:
        :return: a Points object wrapping the point
        """
        points = Points()
        points.positions.update({axis:[point.positions[axis]] for axis in point.positions})
        points.lower.update({axis:[point.lower[axis]] for axis in point.lower})
        points.upper.update({axis:[point.upper[axis]] for axis in point.upper})
        points.delay_after = [point.delay_after]
        points.duration = [point.duration]
        points.indexes = [point.indexes]
        return points

    @staticmethod
    def points_from_axis_point(dim, index, length):
        points = Points()
        dimension_points = {axis: np.full(length, dim.positions[axis][index]) for axis in dim.positions}
        lower, upper = dim.get_bounds(index)
        points.positions.update(dimension_points)
        points.lower.update({axis: np.full(length, lower[axis]) for axis in lower})
        points.upper.update({axis: np.full(length, upper[axis]) for axis in upper})
        points.indexes = np.full(length, index)
        return points
