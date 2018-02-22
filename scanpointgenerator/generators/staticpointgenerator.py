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

from scanpointgenerator.core import Generator

@Generator.register_subclass("scanpointgenerator:generator/StaticPointGenerator:1.0")
class StaticPointGenerator(Generator):
    """Generate 'empty' points with no axis information"""

    def __init__(self, size):
        self.size = size
        self.units = {}
        self.axes = []

    def to_dict(self):
        d = {
                "typeid" : self.typeid,
                "size" : self.size,
            }
        return d

    def prepare_arrays(self, index_array):
        return {}

    @classmethod
    def from_dict(cls, d):
        size = d["size"]
        return cls(size)
