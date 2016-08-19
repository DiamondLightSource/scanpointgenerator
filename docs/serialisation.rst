Serialisation
=============

These generators are designed to be serialised and sent over json. The model
for the CompoundGenerator is as follows::

    {
        type: "CompoundGenerator",
        generators: [
            {
                type: "LineGenerator"
                name: "y"
                units: "mm"
                start: 0.0
                stop: 1.0
                num: 5
                alternate_direction = False
            },
            {
                type: "LineGenerator"
                name: "x"
                units: "mm"
                start: 0.0
                stop: 5.0
                num: 5
                alternate_direction = True
            }
        ],
        excluders: [
            {
                roi: {
                    type: "CircularROI"
                    centre: [0.0, 0.0]
                    radius: 0.5
                }
                scannables: ["x", "y"]
            }
        ],
        mutators: [
            {
                type: "RandomOffsetMutator"
                seed: 10
                axes: ["x", "y"]
                max_offset: {
                        x: 0.1
                        y: 0.2
                }
            }
        ]
    }

The models for each base generator are:

ArrayGenerator (where name and points can be N-dimensional and upper_bounds and lower_bounds are optional)::

    {
        type: "ArrayGenerator"
        name: "x" or ["x", "y"]
        units: "mm"
        points: [1.0, 2.0, 3.0] or [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]]
        upper_bounds: [1.5, 2.5, 3.5]
        lower_bounds: [0.5, 1.5, 2.5]
    }

LineGenerator (name, start and stop can be N-dimensional to create and ND scan)::

    {
        type: "LineGenerator"
        name: "x" or ["x", "y"]
        units: "mm"
        start: 0.0 or [0.0, 0.0]
        num: 5
        alternate_direction = True
    }

LissajousGenerator (where num_points is optional)::

    {
        type: "LissajousGenerator"
        names: ["x", "y"]
        units: "mm"
        box: {
            centre: [0.0, 0.0]
            width: 10.0
            height: 10.0
        }
        num_lobes: 20
        num_points: 1000
    }

SpiralGenerator (where scale is optional)::

    {
        type: Spiralgenerator
        names: ["x", "y"]
        units: "mm"
        centre: [0.0, 0.0]
        radius: 5.0
        scale: 2.0
        alternate_direction = True
    }

And for the mutators:

RandomOffsetMutator::

    {
        type: "RandomOffsetMutator"
        seed: 10
        axes: ["x", "y"]
        max_offset: {
            x: 0.1
            y: 0.2
        }
    }

And the excluders:

    To be added...

As an example of serialising, here is a simple snake scan.

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
