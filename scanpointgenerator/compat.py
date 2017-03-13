###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

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
