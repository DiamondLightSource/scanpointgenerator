from scanpointgenerator import LineGenerator, ZipGenerator, Generator
from tests.test_util import ScanPointGeneratorTest


class ZipGeneratorTest(ScanPointGeneratorTest):

    def test_init(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        g = ZipGenerator([genone])
        self.assertEqual(["x"], g.axes)
        gau = g.axis_units()
        self.assertEqual(dict(x="mm"), gau)
        self.assertEqual(5, g.size)
        self.assertEqual(False, g.alternate)

    def test_init_alternate(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        g = ZipGenerator([genone], True)
        self.assertEqual(["x"], g.axes)
        gau = g.axis_units()
        self.assertEqual(dict(x="mm"), gau)
        self.assertEqual(5, g.size)
        self.assertEqual(True, g.alternate)

    def test_init_diff_axis(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("y", "mm", 13, 20, 5)
        g = ZipGenerator([genone, gentwo])
        self.assertEqual(["x", "y"], g.axes)
        self.assertEqual(dict(x="mm", y="mm"), g.axis_units())
        self.assertEqual(5, g.size)

    def test_init_same_axis(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("x", "mm", 13, 20, 5)
        with self.assertRaises(AssertionError):
            ZipGenerator([genone, gentwo])

    def test_init_diff_size(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("y", "mm", 13, 20, 6)
        with self.assertRaises(AssertionError):
            ZipGenerator([genone, gentwo])

    def test_init_diff_alternate(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5, alternate=True)
        gentwo = LineGenerator("y", "mm", 13, 20, 5, alternate=False)
        with self.assertRaises(AssertionError):
            ZipGenerator([genone, gentwo])

    def test_init_two_dim_line_axis(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        g = ZipGenerator([genone])
        self.assertEqual(["x", "y"], g.axes)
        self.assertEqual(dict(x="mm", y="mm"), g.axis_units())
        self.assertEqual(3, g.size)

    def test_init_two_gen_same_axis(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        gentwo = LineGenerator(["x", "y"], ["mm", "mm"], [6., -6.],
                               [8., -8.], 3)
        with self.assertRaises(AssertionError):
            ZipGenerator([genone, gentwo])

    def test_init_two_gen_diff_axis(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        gentwo = LineGenerator(["w", "z"], ["mm", "mm"], [6., -6.],
                               [8., -8.], 3)
        g = ZipGenerator([genone, gentwo])
        self.assertEqual(["x", "y", "w", "z"], g.axes)
        self.assertEqual(dict(x="mm", y="mm", w="mm", z="mm"), g.axis_units())
        self.assertEqual(3, g.size)

    def test_init_two_gen_overlap_axis(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        gentwo = LineGenerator(["y", "z"], ["mm", "mm"], [6., -6.],
                               [8., -8.], 3)
        with self.assertRaises(AssertionError):
            ZipGenerator([genone, gentwo])

    def test_init_none(self):
        with self.assertRaises(AssertionError):
            ZipGenerator([])

    def test_array_positions_from_line(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("y", "mm", 11, 19, 5)
        genthree = LineGenerator("z", "mm", 21, 29, 5)
        g = ZipGenerator([genone, gentwo, genthree])
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual([1, 3, 5, 7, 9], g.positions['x'].tolist())
        self.assertEqual([0, 2, 4, 6, 8, 10], g.bounds['x'].tolist())
        self.assertEqual([11, 13, 15, 17, 19], g.positions['y'].tolist())
        self.assertEqual([10, 12, 14, 16, 18, 20], g.bounds['y'].tolist())
        self.assertEqual([21, 23, 25, 27, 29], g.positions['z'].tolist())
        self.assertEqual([20, 22, 24, 26, 28, 30], g.bounds['z'].tolist())

    def test_array_positions_from_two_dim_line_axis(self):
        genone = LineGenerator(["x", "y"], ["mm", "mm"], [2., -2.],
                               [4., -4.], 3)
        g = ZipGenerator([genone])
        g.prepare_positions()
        g.prepare_bounds()
        self.assertEqual([2, 3, 4], g.positions['x'].tolist())
        self.assertEqual([1.5, 2.5, 3.5, 4.5], g.bounds['x'].tolist())
        self.assertEqual([-2, -3, -4], g.positions['y'].tolist())
        self.assertEqual([-1.5, -2.5, -3.5, -4.5], g.bounds['y'].tolist())

    def test_to_dict(self):
        genone = LineGenerator("x", "mm", 1.0, 9.0, 5)
        gentwo = LineGenerator("y", "mm", 11, 19, 5)
        g = ZipGenerator([genone, gentwo])

        expected_dict = dict()
        expected_dict['typeid'] = \
            "scanpointgenerator:generator/ZipGenerator:1.0"
        expected_dict['generators'] = [{'typeid': 'scanpointgenerator:generator'
                                                  '/LineGenerator:1.0',
                                        'alternate': False,
                                        'axes': ['x'],
                                        'stop': [9.0],
                                        'start': [1.0],
                                        'units': ['mm'],
                                        'size': 5},
                                       {'typeid': 'scanpointgenerator:generator'
                                                  '/LineGenerator:1.0',
                                        'alternate': False,
                                        'axes': ['y'],
                                        'stop': [19],
                                        'start': [11],
                                        'units': ['mm'],
                                        'size': 5}]
        expected_dict['alternate'] = False

        d = g.to_dict()
        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        _dict = dict()
        _dict['typeid'] = "scanpointgenerator:generator/ZipGenerator:1.0"
        _dict['generators'] = [
            {'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
             'alternate': False,
             'axes': ['x'],
             'stop': [9.0],
             'start': [1.0],
             'units': ['mm'],
             'size': 5},
            {'typeid': 'scanpointgenerator:generator/LineGenerator:1.0',
             'alternate': False,
             'axes': ['y'],
             'stop': [19],
             'start': [11],
             'units': ['mm'],
             'size': 5}]

        gen = ZipGenerator.from_dict(_dict)
        self.assertEqual(["x", "y"], gen.axes)
        self.assertEqual(dict(x="mm", y="mm"), gen.axis_units())
        self.assertEqual(5, gen.size)
        self.assertEqual(False, gen.alternate)
        gen.prepare_positions()
        gen.prepare_bounds()
        self.assertEqual([1, 3, 5, 7, 9], gen.positions['x'].tolist())
        self.assertEqual([0, 2, 4, 6, 8, 10], gen.bounds['x'].tolist())
        self.assertEqual([11, 13, 15, 17, 19], gen.positions['y'].tolist())
        self.assertEqual([10, 12, 14, 16, 18, 20], gen.bounds['y'].tolist())
