from scanpointgenerator.core import Generator
from scanpointgenerator.compat import np


@Generator.register_subclass("scanpointgenerator:generator/PowerTermGenerator:1.0")
class PowerTermGenerator(Generator):
    """
    Generate a line of points according to the function
        y = sign * ((x-xf)/a)**n + yf

        sign is determined by start, stop, focus and exponent parameters
    """

    def __init__(self, axis, units, start, stop, focus, exponent, divisor):
        """
        y = ((x-x_focus)/divisor)**exponent + focus
        Args:
            axis (str): The scannable axis e.g. "dcm_energy"
            units (str): The scannable units e.g. "keV"
            start (float): The first position to be generated.
            stop (float): Will determine scan size. The final generated position will not necessarily be this...
            focus (float): Point of interest which will be most finely sampled
                            e.g. 7.112 (for Fe K edge)
            exponent (int): n in above equation. If exponent is even, it is assumed we pass through the focus point.
            divisor (float): a in the above equation. Sign will be ignored.
        """

        if divisor == 0:
            raise ValueError("Divisor must be non-zero")

        if exponent < 1 or exponent != int(exponent):
            raise ValueError("Exponent must be a positive integer")

        self.sign = get_suitable_sign(start, stop, focus, exponent)
        self.exponent = exponent
        self.divisor = np.abs(divisor)
        self.focus = focus
        self.axes = [axis]
        self.units = {axis: units}
        self.start = start
        self.stop = stop

        self.xc = self.find_xc()  # _fn(xc) = focus
        self.size = int(self._inv_fn(stop))

    def prepare_arrays(self, index_array):
        arrays = dict()
        arrays[self.axes[0]] = self._fn(index_array)
        return arrays

    def _fn(self, x):
        return self.sign * np.power((x - self.xc) / self.divisor, self.exponent) + self.focus

    def _inv_fn(self, y):
        # The dependent variable is point index, which is always positive.
        return self.divisor * np.power(np.abs(y-self.focus), 1./self.exponent) + self.xc

    def find_xc(self):
        self.xc = 0  # temporarily
        return self._inv_fn(self.start)

    def to_dict(self):
        d = dict()
        d['typeid'] = self.typeid
        d['axes'] = self.axes
        d['units'] = self.units[self.axes[0]]
        d['start'] = self.start
        d['stop'] = self.stop
        d['focus'] = self.focus
        d['exponent'] = self.exponent
        d['divisor'] = self.divisor

        return d

    @classmethod
    def from_dict(cls, d):
        axes = d['axes']
        units = d['units']
        start = d['start']
        stop = d['stop']
        exponent = d['exponent']
        divisor = d['divisor']
        focus = d['focus']

        return cls(axes, units, start, stop, focus, exponent, divisor)


def get_suitable_sign(start, stop, focus, exponent):
    if exponent % 2 == 1:
        return 1 if start < stop else -1
    else:
        if focus <= start and focus <= stop:
            return 1
        if focus >= start and focus >= stop:
            return -1
        raise ValueError("Invalid parameters")