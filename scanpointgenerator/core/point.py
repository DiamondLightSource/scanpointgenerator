###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Joseph Ware
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
    
    def extract(self, points):
        self.positions.update(points.positions)
        self.lower.update(points.lower)
        self.upper.update(points.upper)
        if (len(self.indexes)):
            self.indexes = np.column_stack((self.indexes, points.indexes))
        else:
            self.indexes = points.indexes
        
    @staticmethod
    def points_from_axis_points(axis_point, index, length):
        points = Points()
        for axis in axis_point:
            dimension_points = {axis:np.full(length, axis_point[axis])}
            points.positions.update(dimension_points)
            points.lower.update(dimension_points)
            points.upper.update(dimension_points)
        points.indexes = np.full(length, index)
        return points
    