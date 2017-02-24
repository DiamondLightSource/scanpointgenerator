from scanpointgenerator.compat import np


class Generator(object):
    """Base class for all malcolm scan point generators

    Attributes:
        units (dict): Dict of str position_name -> str position_unit
            for each scannable dimension. E.g. {"x": "mm", "y": "mm"}
        index_dims (list): List of the int dimension sizes for the dataset. This
            will have the same length as the units list for square
            scans but will be shorter for things like spiral scans. E.g. [15]
        index_names (list): List of the str dimension names for the dataset.
            This will have the same length as the index_dims. E.g. ["spiral_i"]
        axes (list): List of scannable names, used in GDA to reconstruct Point
            in CompoundGenerators
    """
    alternate = False
    units = None
    index_dims = None
    index_names = None
    positions = None
    bounds = None
    size = 0
    # Lookup table for generator subclasses
    _generator_lookup = {}
    axes = []

    def prepare_arrays(self, index_array):
        """
        Abstract method to create position or bounds array from provided index
        array. index_array will be np.arange(self.size) for positions and
        np.arange(self.size + 1) - 0.5 for bounds.

        Args:
            index_array (np.array): Index array to produce parameterised points

        Returns:
            Positions: Dictionary of axis names to position/bounds arrays
        """
        raise NotImplementedError

    def prepare_positions(self):
        self.positions = self.prepare_arrays(np.arange(self.size))

    def prepare_bounds(self):
        self.bounds = self.prepare_arrays(np.arange(self.size + 1) - 0.5)

    def to_dict(self):
        """Abstract method to convert object attributes into a dictionary"""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d):
        """
        Abstract method to create a ScanPointGenerator instance from a
        serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            Generator: New ScanPointGenerator instance
        """

        generator_type = d["typeid"]
        generator = cls._generator_lookup[generator_type]
        assert generator is not cls, \
            "Subclass %s did not redefine from_dict" % generator_type
        gen = generator.from_dict(d)
        return gen

    @classmethod
    def register_subclass(cls, generator_type):
        """
        Register a subclass so from_dict() works

        Args:
            generator_type (Generator): Subclass to register
        """

        def decorator(generator):

            cls._generator_lookup[generator_type] = generator
            generator.typeid = generator_type

            return generator
        return decorator
