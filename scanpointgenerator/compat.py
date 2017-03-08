import os

try:
    range_ = xrange
except NameError:
    # For Python3
    range_ = range


if os.name == 'java':
    import numjy as numpy
else:
    import numpy

np = numpy
