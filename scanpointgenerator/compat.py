import os

try:
    range_ = xrange
except NameError:
    # For Python3
    range_ = range


if os.name == 'java':
    import scisoftpy as numpy
else:
    import numpy

np = numpy
