from scanpointgenerator import LineGenerator, NestedGenerator, plot_generator

xs = LineGenerator("x", "mm", 0, 0.1, 5)
ys = LineGenerator("y", "mm", 1, 0.1, 4)
gen = NestedGenerator(ys, xs, snake=True)
plot_generator(gen)