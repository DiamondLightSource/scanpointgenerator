import numpy
from annotypes import Anno, deserialize_object, Array
from scanpointgenerator.core import Generator, AAlternate

with Anno("The array containing points"):
    AGenerator = Array[Generator]


@Generator.register_subclass(
    "scanpointgenerator:generator/MergeGenerator:1.0")
class MergeGenerator(Generator):
    """ Merge generators to operate one after each other"""

    def __init__(self, generators, alternate=False):
        # type: (AGenerator, AAlternate) -> None
        super(MergeGenerator, self).__init__(axes="x",
                                             size=1,
                                             units="mm",
                                             alternate=alternate)
        self.generators = AGenerator([deserialize_object(g, Generator)
                                      for g in generators])
        self.units = self.generators[0].units
        self.axes = self.generators[0].axes
        self.size = sum(generator.size for generator in self.generators)
        for generator in self.generators:
            assert generator.axes == self.axes, "You cannot merge generators " \
                                                "on different axes"
            assert generator.units == self.units, "You cannot merge " \
                                                  "generators with different" \
                                                  " units"

    def prepare_arrays(self, index_array):
        # The MergeGenerator gets its positions from its sub-generators
        mergearrays = {}
        for axis in self.axes:
            mergearrays[axis] = []
        count = 1
        sizetotal = 0
        for generator in self.generators:
            if count >= len(self.generators):
                arrays = generator.prepare_arrays(index_array[0:len(index_array)
                                                              - sizetotal])
            else:
                sizetotal += generator.size
                arrays = generator.prepare_arrays(index_array[0:generator.size])
                count += 1
            for axis in self.axes:
                currentarray = mergearrays[axis]
                currentarray = numpy.append(currentarray, arrays[axis])
                mergearrays[axis] = currentarray
        return mergearrays
