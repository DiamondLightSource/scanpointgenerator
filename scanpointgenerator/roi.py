

class ROI(object):

    _roi_lookup = {}

    def __init__(self, name, centre):

        self.name = name
        self.centre = centre

    def contains_point(self, point):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d):
        """
        Abstract method to create a ROI instance from a
        serialised dictionary

        Args:
            d(dict): Dictionary of attributes

        Returns:
            ROI: New ROI instance
        """

        roi_type = d["type"]
        roi = cls._roi_lookup[roi_type]
        assert roi is not cls, \
            "Subclass %s did not redefine from_dict" % roi_type
        r = roi.from_dict(d)
        return r

    @classmethod
    def register_subclass(cls, roi_type):
        """
        Register a subclass so from_dict() works

        Args:
            roi_type (ROI): Subclass to register
        """

        def decorator(roi):

            cls._roi_lookup[roi_type] = roi

            return roi
        return decorator
