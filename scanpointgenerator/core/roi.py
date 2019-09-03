###
# Copyright (c) 2016 Diamond Light Source Ltd.
#
# Contributors:
#    Tom Cobb - initial API and implementation and/or initial documentation
#    Gary Yendell - initial API and implementation and/or initial documentation
#    Charles Mita - initial API and implementation and/or initial documentation
#
###

from annotypes import Serializable


class ROI(Serializable):

    def __init__(self):
        # type: () -> None
        pass

    def contains_point(self, point):
        raise NotImplementedError
