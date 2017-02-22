from scanpointgenerator.core import Mutator


@Mutator.register_subclass("scanpointgenerator:mutator/FixedDurationMutator:1.0")
class FixedDurationMutator(Mutator):
    """Mutator to apply a fixed duration to points of a ScanPointGenerator"""

    def __init__(self, duration):
        """Args:
            duration(float): Duration to apply
        """
        self.duration = duration

    def mutate(self, point, index):
        """
        Applies duration to points in the given iterator, yielding them

        Args:
            Point: Point to mutate
            Index: one-dimensional index of point

        Returns:
            Point: Mutated point
        """

        point.duration = self.duration
        return point

    def to_dict(self):
        return {"typeid": self.typeid, "duration": self.duration}

    @classmethod
    def from_dict(cls, d):
        return cls(d["duration"])
