from linegenerator import LineGenerator


class StepLineGenerator(LineGenerator):

    def __init__(self, name, units, start, end, step):

        num = int((end - start)/step) + 1

        super(StepLineGenerator, self).__init__(name, units, start, step, num)
