import unittest
from scanpointgenerator import LineGenerator, ConcatGenerator, ArrayGenerator, \
    CompoundGenerator
from tests.test_util import ScanPointGeneratorTest


class ConcatGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 13, 20, 5)
        g = ConcatGenerator([genone, gentwo])
        self.assertEqual(["x"], g.axes)
        self.assertEqual(dict(x="mm"), g.axis_units())
        self.assertEqual(10, g.size)

    def test_init_none(self):
        with self.assertRaises(AssertionError):
            ConcatGenerator([])

    def test_init_alternate(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 13, 20, 5)
        g = ConcatGenerator([genone, gentwo], True)
        self.assertEqual(["x"], g.axes)
        self.assertEqual(dict(x="mm"), g.axis_units())
        self.assertEqual(10, g.size)
        self.assertEqual(True, g.alternate)

    def test_init_two_dim(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        gentwo = LineGenerator(["x", "y"], ["mm", "mm"], [6., -6.],
                               [8., -8.], 3)
        g = ConcatGenerator([genone, gentwo])
        self.assertEqual(["x", "y"], g.axes)
        self.assertEqual({"x": "mm", "y": "mm"}, g.axis_units())

    def test_init_alternate_set(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate=True)
        gentwo = LineGenerator("x", "mm", 13, 20, 5, alternate=True)
        with self.assertRaises(AssertionError):
            ConcatGenerator([genone, gentwo])

    def test_array_positions_from_line(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 11, 19, 5)
        g = ConcatGenerator([genone, gentwo])
        positions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        bounds = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(positions, g.positions['x'].tolist())
        self.assertEqual(bounds, g.bounds['x'].tolist())

    def test_array_positions_from_array(self):
        genone = ArrayGenerator("x", "mm", [1.0, 2.0, 3.0, 4.0, 5.0])
        gentwo = ArrayGenerator("x", "mm", [6.0, 7.0, 8.0, 9.0, 0.0])
        g = ConcatGenerator([genone, gentwo])
        positions = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 0.0]
        bounds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 4.5, -4.5]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(positions, g.positions['x'].tolist())
        self.assertEqual(bounds, g.bounds['x'].tolist())

    def test_array_positions_from_2D_line(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        gentwo = LineGenerator(["x", "y"], ["mm", "mm"], [5., -4.],
                               [7., -2.], 3)
        g = ConcatGenerator([genone, gentwo])
        x_positions = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        y_positions = [-2.0, -3.0, -4.0, -4.0, -3.0, -2.0]
        x_bounds = [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
        y_bounds = [-1.5, -2.5, -3.5, -4.5, -3.5, -2.5, -1.5]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(x_positions, g.positions['x'].tolist())
        self.assertEqual(y_positions, g.positions['y'].tolist())
        self.assertEqual(x_bounds, g.bounds['x'].tolist())
        self.assertEqual(y_bounds, g.bounds['y'].tolist())

    def test_array_positions_from_three_(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 11, 19, 5)
        genthree = LineGenerator("x", "mm", 21, 29, 5)
        g = ConcatGenerator([genone, gentwo, genthree])
        positions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        bounds = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual(positions, g.positions['x'].tolist())
        self.assertEqual(bounds, g.bounds['x'].tolist())

    def test_array_positions_from_line_non_matching_bounds(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 20, 24, 5)
        g = ConcatGenerator([genone, gentwo])
        g.prepare_positions()
        with self.assertRaises(AssertionError):
            g.prepare_bounds()

    def test_array_positions_from_three_line_non_matching_bounds(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 11, 19, 5)
        genthree = LineGenerator("x", "mm", 22, 30, 5)
        g = ConcatGenerator([genone, gentwo, genthree])
        g.prepare_positions()
        with self.assertRaises(AssertionError):
            g.prepare_bounds()

    def test_to_dict(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 13, 20, 5)
        g = ConcatGenerator([genone, gentwo])
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/ConcatGenerator:1.0"
        expected_dict['generators'] = [{'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
                                        'alternate': False,
                                        'axes': ['x'],
                                        'stop': [9.0],
                                        'start': [1.0],
                                        'units': ['mm'],
                                        'size': 5},
                                       {'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
                                        'alternate': False,
                                        'axes': ['x'],
                                        'stop': [20],
                                        'start': [13],
                                        'units': ['mm'],
                                        'size': 5}]
        expected_dict['alternate'] = False
        d = g.to_dict()
        self.assertEqual(expected_dict, d)
        comp = CompoundGenerator([g], [], [])
        expected_dict = dict()
        expected_dict['typeid'] = "scanpointgenerator:generator/CompoundGenerator:1.0"
        expected_dict['generators'] = [{'typeid': 'scanpointgenerator:generator/ConcatGenerator:1.0',
                                        'alternate': False,
                                        'generators': [{'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
                                                        'alternate': False,
                                                        'axes': ['x'],
                                                        'stop': [9.0],
                                                        'start': [1.0],
                                                        'units': ['mm'],
                                                        'size': 5},
                                                       {'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
                                                        'alternate': False,
                                                        'axes': ['x'],
                                                        'stop': [20],
                                                        'start': [13],
                                                        'units': ['mm'],
                                                        'size': 5}]}]
        expected_dict['excluders'] = []
        expected_dict['mutators'] = []
        expected_dict['duration'] = -1.0
        expected_dict['continuous'] = True
        expected_dict['delay_after'] = 0
        d = comp.to_dict()
        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        g1_dict = genone.to_dict()
        gentwo = LineGenerator("x", "mm", 13, 20, 5)
        g2_dict = gentwo.to_dict()
        _dict = dict()
        _dict['generators'] = [g1_dict, g2_dict]
        _dict['alternate'] = False
        gen = ConcatGenerator.from_dict(_dict)
        self.assertEqual(gen.generators[0].to_dict(), genone.to_dict())
        self.assertEqual(gen.generators[1].to_dict(), gentwo.to_dict())

        g = ConcatGenerator([genone, gentwo])
        g_dict = g.to_dict()
        _dict = dict()
        _dict['generators'] = [g_dict]
        _dict['excluders'] = []
        _dict['mutators'] = []
        _dict['duration'] = 10
        _dict['continuous'] = False
        gen = CompoundGenerator.from_dict(_dict)
        self.assertEqual(gen.generators[0].to_dict(), g.to_dict())

    def test_compound_of_two_lines(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 11, 19, 5)
        lines = ConcatGenerator([genone, gentwo])
        g = CompoundGenerator([lines], [], [], duration=0.5)
        g.prepare()
        x_positions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        expected_pos = []
        for i in range(len(x_positions)):
            expected_pos.append({"x": x_positions[i]})
        points = list(g.iterator())
        self.assertEqual(expected_pos, [p.positions for p in points])
        data = []
        for vals in expected_pos:
            data.append(vals["x"])

    def test_concat_three_oneD_lines(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 11, 19, 5)
        genthree = LineGenerator("x", "mm", 19.5, 13.5, 7)
        lines = ConcatGenerator([genone, gentwo, genthree])
        g = CompoundGenerator([lines], [], [], duration=0.5)
        x_positions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 19.5, 18.5, 17.5,
                       16.5, 15.5, 14.5, 13.5]
        expected_pos = []
        for i in range(len(x_positions)):
            expected_pos.append({"x": x_positions[i]})
        g.prepare()
        points = list(g.iterator())
        self.assertEqual(expected_pos, [p.positions for p in points])

    def test_concat_three_twoD_lines(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [1.0, 12.0],
                               [9.0, 4.0], 5)
        gentwo = LineGenerator(["x", "y"], ["mm", "mm"], [11.0, 4.0],
                               [19.0, 12.0], 5)
        genthree = LineGenerator(["x", "y"], ["mm", "mm"], [19.5, 13.5],
                                 [13.5, 19.5], 7)

        lines = ConcatGenerator([genone, gentwo, genthree])

        g = CompoundGenerator([lines], [], [], duration=0.5)
        x_positions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 19.5, 18.5, 17.5,
                       16.5,  15.5, 14.5, 13.5]
        y_positions = [12, 10, 8, 6, 4, 4, 6, 8, 10, 12, 13.5, 14.5, 15.5, 16.5,
                       17.5, 18.5, 19.5]
        expected_pos = []
        for i in range(len(x_positions)):
            expected_pos.append({"x": x_positions[i], "y": y_positions[i]})
        g.prepare()
        points = list(g.iterator())
        self.assertEqual(expected_pos, [p.positions for p in points])

    def test_concat_five_twoD_lines(self):
        lineone = LineGenerator(["x", "y"], ["mm", "mm"], [0, 0], [10, 10], 6)
        linetwo = LineGenerator(["x", "y"], ["mm", "mm"], [12, 11], [22, 11], 6)
        linethree = LineGenerator(["x", "y"], ["mm", "mm"], [24, 10],
                                  [34, 0], 6)
        linefour = LineGenerator(["x", "y"], ["mm", "mm"], [32.5, -1], [2.5, -1], 7)
        linefive = LineGenerator(["x", "y"], ["mm", "mm"], [5, 1], [55, 21], 6)

        lines = ConcatGenerator([lineone, linetwo, linethree,
                                linefour, linefive])
        g = CompoundGenerator([lines], [], [], duration=0.5)
        x_positions = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20,
                       22, 24, 26, 28, 30, 32, 34, 32.5, 27.5, 22.5, 17.5, 12.5,
                       7.5, 2.5, 5.0, 15.0, 25, 35, 45, 55]
        y_positions = [0, 2, 4, 6, 8, 10, 11, 11, 11, 11, 11, 11, 10,
                       8, 6, 4, 2, 0,  -1, -1, -1, -1, -1, -1, -1, 1, 5,
                       9, 13, 17, 21]
        expected_pos = []
        for i in range(len(x_positions)):
            expected_pos.append({"x": x_positions[i], "y": y_positions[i]})
        g.prepare()
        points = list(g.iterator())
        self.assertEqual(expected_pos, [p.positions for p in points])


if __name__ == "__main__":
    unittest.main(verbosity=2)
