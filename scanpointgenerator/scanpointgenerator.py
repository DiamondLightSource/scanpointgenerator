class ScanPointGenerator(object):
    """Base class for all malcolm scan point generators

    Attributes:
        position_names (list): List of str names for each scannable, fastest
            changing last. E.g. ["y", "x"]
        position_units (list): List of str units for each scannable, fastest
            changing last. E.g. ["mm", "mm"]
        index_dims (list): List of the int dimension sizes for the dataset. This
            will have the same length as the position_names list for square
            scans but will be shorter for things like spiral scans. E.g. [15]
    """
    position_names = None
    position_units = None
    index_dims = None

    def positions(self):
        """An iterator yielding demand positions at each scan point

        Yields:
            list: The next scan point. This is a list of float demand positions
                for each position_name
        """
        raise NotImplementedError

    def indexes(self):
        """An iterator yielding dataset indexes at each scan point

        Yields:
            list: The next scan point. This is a list of int dataset indexes
                that the current frame should be written to
        """
        raise NotImplementedError

    def bounds(self):
        """An iterator yielding lower and upper position bounds for each scan
        point

        Yields:
            list: The upper and lower bounds next scan point. This is a list of
                (float lower, float upper) tuples for each position_name
        """
        raise NotImplementedError
