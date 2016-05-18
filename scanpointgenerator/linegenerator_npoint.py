from linegenerator import LineGenerator


class NPointLineGenerator(LineGenerator):

    def __init__(self, name, units, start, end, num):

        step = (end - start)/num
        start += step/2

        super(NPointLineGenerator, self).__init__(name, units, start, step, num)
