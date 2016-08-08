Serialisation
=============

These generators are designed to be serialised and sent over json. The model
is as follows::

    {
        type: 'CompoundGenerator',
        generators: [
            {
                type: LineGenerator
                name: y
                units: mm
                start: 0.0
                stop: 1.0
                num: 5
                alternate_direction = False
            },
            {
                type: LineGenerator
                name: x
                units: mm
                start: 0.0
                stop: 5.0
                num: 5
                alternate_direction = True
            }
        ],
        excluders: [
            {
                roi: {
                    type: CircularROI
                    centre: [0.0, 0.0]
                    radius: 0.5
                }
                scannables: ['x', 'y']
            }
        ],
        mutators: [
            {
                type: RandomOffsetMutator
                seed: 10
                max_offset: {
                        x: 0.1
                        y: 0.2
                }
            }
        ]
    }

As an example, here is a simple snake scan.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
        plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([y, x], [], [])

    plot_generator(gen)

It is the same after being serialised and deserialised.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator, \
        plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate_direction=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([y, x], [], [])

    gen_dict = gen.to_dict()
    new_gen = CompoundGenerator.from_dict(gen_dict)

    plot_generator(new_gen)
