Serialisation
=============

These generators are designed to be serialised and sent over json. The model
for the CompoundGenerator is as follows::

    {
        typeid: "scanpointgenerator:generator/CompoundGenerator:1.0",
        generators: [
            {
                typeid: "scanpointgenerator:generator/LineGenerator:1.0"
                axes: "y"
                units: "mm"
                start: 0.0
                stop: 1.0
                size: 5
                alternate = False
            },
            {
                typeid: "scanpointgenerator:generator/LineGenerator:1.0"
                axes: "x"
                units: "mm"
                start: 0.0
                stop: 5.0
                size: 5
                alternate = True
            }
        ],
        excluders: [
            {
                roi: {
                    typeid: "scanpointgenerator:roi/CircularROI:1.0"
                    centre: [0.0, 0.0]
                    radius: 0.5
                }
                scannables: ["x", "y"]
            }
        ],
        mutators: [
            {
                typeid: "scanpointgenerator:mutator/RandomOffsetMutator:1.0"
                seed: 10
                axes: ["x", "y"]
                max_offset: {
                        x: 0.1
                        y: 0.2
                }
            }
        duration: -1.0
        ]
    }

The models for each base generator are:

LineGenerator (axes, start and stop can be N-dimensional to create and ND scan)::

    {
        typeid: "scanpointgenerator:generator/LineGenerator:1.0"
        axes: "x" or ["x", "y"]
        units: "mm" or ["mm", "mm"]
        start: 0.0 or [0.0, 0.0]
        size: 5
        alternate = True
    }

LissajousGenerator::

    {
        typeid: "scanpointgenerator:generator/LissajousGenerator:1.0"
        axes: ["x", "y"]
        units: ["mm", "mm"]
        centre: [0.0, 0.0]
        span: [10.0, 10.0]
        lobes: 20
        size: 1000
        alternate = False
    }

SpiralGenerator::

    {
        typeid: "scanpointgenerator:generator/SpiralGenerator:1.0"
        axes: ["x", "y"]
        units: ["mm", "mm"]
        centre: [0.0, 0.0]
        radius: 5.0
        scale: 2.0
        alternate = True
    }

ArrayGenerator::

    {
        typeid: "scanpointgenerator:generator/ArrayGenerator:1.0"
        axis: "x"
        units: "mm"
        points: [0., 1., 1.5, 2.]
        alternate = True
    }

And for the mutators:

RandomOffsetMutator::

    {
        typeid: "scanpointgenerator:mutator/RandomOffsetMutator:1.0"
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

    from scanpointgenerator import LineGenerator, CompoundGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([y, x], [], [])

    plot_generator(gen)

It is the same after being serialised and deserialised.

.. plot::
    :include-source:

    from scanpointgenerator import LineGenerator, CompoundGenerator
    from scanpointgenerator.plotgenerator import plot_generator

    x = LineGenerator("x", "mm", 0.0, 4.0, 5, alternate=True)
    y = LineGenerator("y", "mm", 0.0, 3.0, 4)
    gen = CompoundGenerator([y, x], [], [])

    gen_dict = gen.to_dict()
    new_gen = CompoundGenerator.from_dict(gen_dict)

    plot_generator(new_gen)
