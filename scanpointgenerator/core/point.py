###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#
###

class Point(object):
    """Contains information about for each scan point

    Attributes:
        positions (dict): Dict of str position_name -> float position for each
            scannable dimension. E.g. {"x": 0.1, "y": 2.2}
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
