from scanpointgenerator.core import Generator
from scanpointgenerator.compat import np


@Generator.register_subclass("scanpointgenerator:generator/PowerTermGenerator:1.0")
class PowerTermGenerator(Generator):
    """Generate a line of points according to the function y = ((x-x_focus)/divisor)**exponent + focus"""

    def __init__(self, axis, units, start, stop, focus, exponent, divisor):
        """
        Args:
            axis (str): The scannable axis e.g. "dcm_energy"
            units (str): The scannable units e.g. "keV"
            start (float): The first position to be generated.
            stop (float): Will determine scan size. The final generated position will not necessarily be this...
            focus (float): Point of interest which will be most finely sampled
                            e.g. 7.112 (for Fe K edge)
            exponent (int): If exponent is even, it is assumed we pass through the focus point.
            divisor (float): Sign will be ignored.
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

        self.xf = self.find_xf()
        self.size = int(self._inv_fn(stop))+1

    def prepare_arrays(self, index_array):
        arrays = dict()
        arrays[self.axes[0]] = self._fn(index_array)
        return arrays

    def _fn(self, x):
        return self.sign * np.power((x - self.xf) / self.divisor, self.exponent) + self.focus

    def _inv_fn(self, y):
        nth_root = np.power(np.abs(y-self.focus), 1./self.exponent)
        if not self.stop_after_focus():
            nth_root *= -1
        return self.divisor * nth_root + self.xf

    def find_xf(self):
        x = self.divisor * np.power(np.abs(self.start-self.focus), 1./self.exponent)
        return x if self.start_before_focus() else -x

    def start_before_focus(self):
        if self.exponent % 2 == 0:
            return True
        return self.sign * self.start < self.sign * self.focus

    def stop_after_focus(self):
        if self.exponent % 2 == 0:
            return True
        return self.sign * self.stop > self.sign * self.focus

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
        raise ValueError("For even exponents, focus point must be either lowest or highest value")
