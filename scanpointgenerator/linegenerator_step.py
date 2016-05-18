from linegenerator import LineGenerator
import math as m


class StepLineGenerator(LineGenerator):

    def __init__(self, name, units, start, end, step):

        num = int(m.floor((end - start)/step))

        super(StepLineGenerator, self).__init__(name, units, start, step, num)
