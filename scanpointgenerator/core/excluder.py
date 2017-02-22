

class Excluder(object):

    """Base class for objects that filter points based on their attributes."""

    # Lookup table for mutator subclasses
    _excluder_lookup = {}

    def __init__(self, axes):
        """
        Args:
            axes(list(str)): Names of axes to exclude points from

        """
        self.axes = axes

    def create_mask(self, x_points, y_points):
        raise NotImplementedError("Method must be implemented in child class.")

    def to_dict(self):
        """Construct dictionary from attributes."""
        d = dict()
        d['axes'] = self.axes

        return d

    @classmethod
    def from_dict(cls, d):
        """Create an Excluder instance from a serialised dictionary.

        Args:
            d(dict): Dictionary of attributes

        Returns:
            Mutator: New Mutator instance

        """
        excluder_type = d["typeid"]
        excluder = cls._excluder_lookup[excluder_type]
        assert excluder is not cls, \
            "Subclass %s did not redefine from_dict" % excluder_type
        excluder = excluder.from_dict(d)

        return excluder

    @classmethod
    def register_subclass(cls, excluder_type):
        """
        Register a subclass so from_dict() works

        Args:
            excluder_type(Excluder): Subclass to register

        """
        def decorator(excluder):
            cls._excluder_lookup[excluder_type] = excluder
            excluder.typeid = excluder_type

            return excluder

        return decorator
