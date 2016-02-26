class ScanPointGenerator(object):
    """Base class for all malcolm scan point generators

    Attributes:
        position_units (dict): Dict of str position_name -> str position_unit
            for each scannable dimension. E.g. {"x": "mm", "y": "mm"}
        index_dims (list): List of the int dimension sizes for the dataset. This
            will have the same length as the position_names list for square
            scans but will be shorter for things like spiral scans. E.g. [15]
        index_names (list): List of the str dimension names for the dataset.
            This will have the same length as the index_dims. E.g. ["spiral_i"]
    """
    position_units = None
    index_dims = None
    index_names = None

    def iterator(self):
        """An iterator yielding positions at each scan point

        Yields:
            Point: The next scan :class:`Point`
        """
        raise NotImplementedError
