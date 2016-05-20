import unittest

from scanpointgenerator.spiralgenerator import SpiralGenerator


class SpiralGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.g = SpiralGenerator(['x', 'y'], "mm", [0.0, 0.0], 20.0)

    def test_init(self):
        self.assertEqual(self.g.position_units, dict(x="mm", y="mm"))
        self.assertEqual(self.g.index_dims, [7])
        self.assertEqual(self.g.index_names, ["x", "y"])

    def test_iterator(self):
        positions = [{'y': 1.7198356548572724, 'x': 2.678485334011638},
                     {'y': 0.7019932639954504, 'x': 4.446508988608095},
                     {'y': -0.8851945906513048, 'x': 5.44176309934409},
                     {'y': -2.649273043541309, 'x': 5.78876720880193},
                     {'y': -4.393517125295899, 'x': 5.599785629013004},
                     {'y': -6.002930347374706, 'x': 4.975694668081077},
                     {'y': -7.407453441741234, 'x': 4.006801973902928}]
        lower = [{'y': 1.7111515375436872, 'x': 1.4621968395803508},
                 {'y': 1.3223111531820189, 'x': 3.667379276884395},
                 {'y': -0.052052076183252145, 'x': 5.032652033664703},
                 {'y': -1.7600166241951354, 'x': 5.689003054786927},
                 {'y': -3.5323948542229755, 'x': 5.754712784571532},
                 {'y': -5.220261274246597, 'x': 5.336246174220889},
                 {'y': -6.733948439878628, 'x': 4.529095690816852}]
        upper = [{'y': 1.3223111531820189, 'x': 3.667379276884395},
                 {'y': -0.052052076183252145, 'x': 5.032652033664703},
                 {'y': -1.7600166241951354, 'x': 5.689003054786927},
                 {'y': -3.5323948542229755, 'x': 5.754712784571532},
                 {'y': -5.220261274246597, 'x': 5.336246174220889},
                 {'y': -6.733948439878628, 'x': 4.529095690816852},
                 {'y': -8.018990918569312, 'x': 3.41857753746441}]
        indexes = [1, 2, 3, 4, 5, 6, 7]
        for i, p in enumerate(self.g.iterator()):
            self.assertEqual(p.positions, positions[i])
            self.assertEqual(p.lower, lower[i])
            self.assertEqual(p.upper, upper[i])
            self.assertEqual(p.indexes, [indexes[i]])
        self.assertEqual(i, 6)
