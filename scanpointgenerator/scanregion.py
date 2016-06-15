

class ScanRegion(object):
    """
    A class representing a 2D region of interest within an ND scan
    """

    def __init__(self, roi, scannables):

        self.roi = roi
        self.scannables = scannables

    def contains_point(self, d):
        """
        Create a 2D sub-point from the ND point d and pass the sub_point to
        the roi to check if it contains it.

        Args:
            d(dict): Dictionary representation of point

        Returns:
            bool: Whether roi contains the given point
        """

        scannable_1 = d[self.scannables[0]]
        scannable_2 = d[self.scannables[1]]

        sub_point = (scannable_1, scannable_2)

        return self.roi.contains_point(sub_point)
