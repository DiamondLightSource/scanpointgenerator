from annotypes import Anno, deserialize_object, Array
from scanpointgenerator.compat import np
from scanpointgenerator.core import Generator, AAlternate

with Anno("The array containing points"):
    AGenerator = Array[Generator]


@Generator.register_subclass(
    "scanpointgenerator:generator/ConcatGenerator:1.0")
class ConcatGenerator(Generator):
    """ Concat generators to operate one after each other """
    DIFF_LIMIT = 1e-05

    def __init__(self, generators, alternate=False):
        # type: (AGenerator, AAlternate) -> None
        self.generators = AGenerator([deserialize_object(g, Generator)
                                      for g in generators])

        assert len(self.generators) > 0, "At least one generator needed"

        units = self.generators[0].units
        axes = self.generators[0].axes
        size = sum(generator.size for generator in self.generators)
        for generator in self.generators:
            assert generator.axes == axes, "You cannot Concat generators " \
                                                "on different axes"
            assert generator.units == units, "You cannot Concat " \
                                             "generators with different units"
            assert not generator.alternate, \
                "Alternate should not be set on the component generators of a" \
                "ConcatGenerator. Set it on the top level ConcatGenerator only."
        super(ConcatGenerator, self).__init__(axes=axes,
                                              size=size,
                                              units=units,
                                              alternate=alternate)

    def prepare_arrays(self, index_array):
        # The ConcatGenerator gets its positions from its sub-generators
        merged_arrays = {}
        for axis in self.axes:
            merged_arrays[axis] = np.array
        first = True

        if index_array.size == self.size + 1:
            # getting bounds
            preparing_bounds = True
        else:
            # getting positions
            preparing_bounds = False

        for generator in self.generators:

            if preparing_bounds:
                # getting bounds
                arr = generator.prepare_arrays(index_array[:generator.size + 1])
            else:
                # getting positions
                arr = generator.prepare_arrays(index_array[:generator.size])

            for axis in self.axes:
                axis_array = arr[axis]
                if first:
                    merged_arrays[axis] = axis_array
                else:
                    # This avoids appending an ndarray to a list
                    cur_array = merged_arrays[axis]

                    if preparing_bounds:
                        assert np.abs(cur_array[-1] - axis_array[0]) < self.DIFF_LIMIT, \
                                          "Merged generator bounds don't meet" \
                                          " for axis %s (%f, %f)" \
                                          % (str(axis), cur_array[-1],
                                             axis_array[0])
                        cur_array = np.append(cur_array[:-1], axis_array)
                    else:
                        cur_array = np.append(cur_array, axis_array)
                    merged_arrays[axis] = cur_array
            first = False

        return merged_arrays
