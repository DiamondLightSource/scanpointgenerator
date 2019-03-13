###
# Copyright (c) 2017 Diamond Light Source Ltd.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from scanpointgenerator.core import Generator, ASize


@Generator.register_subclass(
    "scanpointgenerator:generator/StaticPointGenerator:1.0")
class StaticPointGenerator(Generator):
    """Generate 'empty' points with no axis information"""
    def __init__(self, size):
        # type: (ASize) -> None
        super(StaticPointGenerator, self).__init__(axes=[], units=[], size=size)

    def prepare_arrays(self, index_array):
        return {}
