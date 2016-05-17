import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import ScanPointGenerator


class ScanPointGeneratorBaseTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = ScanPointGenerator()

    def test_init(self):
        self.assertEqual(self.g.position_units, None)
        self.assertEqual(self.g.index_dims, None)
        self.assertEqual(self.g.index_names, None)
        self.assertRaises(NotImplementedError, self.g.iterator)


if __name__ == "__main__":
    unittest.main()
