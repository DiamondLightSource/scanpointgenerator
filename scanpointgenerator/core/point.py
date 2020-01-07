###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
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
        ''' input:
        other (Point or Points)
        Adds the positions, bounds, ind[ex/ices] of the other object to self, maintaining duration, delay_after
        returns: self
        '''
        self.positions = {axis: self.positions[axis]+other.positions[axis] for axis in self.positions}
        self.upper = {axis: self.upper[axis]+other.upper[axis] for axis in self.upper}
        self.lower = {axis: self.lower[axis]+other.lower[axis] for axis in self.lower}
        if len(self):
            self.indexes += other.indexes
        else:
            self.indexes = other.indexes
        return self

    def __getitem__(self, sliced):
        ''' input:
        sliced (int or slice)- index of a Point or a slice of many Point to consolidate into a Points
        returns: Point or Points object with each field reduced to the relevant indices
        '''
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
        self.positions.update(points.positions)
        self.lower.update(points.lower)
        self.upper.update(points.upper)
        if len(self.indexes):  # if indices is not empty: assumption that length of indices is consistent
            self.indexes = np.column_stack((self.indexes, points.indexes))
        else:
            self.indexes = points.indexes
        
    @staticmethod
    def points_from_axis_points(axis_point, index, length):
        points = Points()
        dimension_points = {axis:np.full(length, axis_point[axis]) for axis in axis_point}
        points.positions.update(dimension_points)
        points.lower.update(dimension_points)
        points.upper.update(dimension_points)
        points.indexes = np.full(length, index)
        return points
