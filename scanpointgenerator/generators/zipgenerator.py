from annotypes import Anno, deserialize_object, Array, Sequence, Union
from scanpointgenerator.core import Generator, AAlternate

with Anno("List of Generators to zip"):
    AGenerators = Array[Generator]
UGenerators = Union[AGenerators, Sequence[Generator], Generator]


@Generator.register_subclass(
    "scanpointgenerator:generator/ZipGenerator:1.0")
class ZipGenerator(Generator):
    """ Zip generators together, combining all generators into one """

    def __init__(self, generators, alternate=False):
        # type: (UGenerators, AAlternate) -> None
        self.generators = AGenerators([deserialize_object(g, Generator)
                                      for g in generators])

        assert len(self.generators), "At least one generator needed"

        units = []
        axes = []
        size = self.generators[0].size

        for generator in self.generators:
            assert generator.axes not in axes, "You cannot zip generators " \
                                               "on the same axes"
            assert generator.size == size, "You cannot zip generators " \
                                           "of different sizes"
            assert not generator.alternate, \
                "Alternate should not be set on the component generators of a" \
                "zip generator. Set it on the top level ZipGenerator only."

            axes += generator.axes
            units += generator.units

        super(ZipGenerator, self).__init__(axes=axes,
                                           size=size,
                                           units=units,
                                           alternate=alternate)

    def prepare_arrays(self, index_array):
        # The ZipGenerator gets its positions from its sub-generators
        zipped_arrays = {}

        for generator in self.generators:
            arrays = generator.prepare_arrays(index_array)
            zipped_arrays.update(arrays)

        return zipped_arrays
