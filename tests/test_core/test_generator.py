import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import Generator

from pkg_resources import require
require("mock")
from mock import MagicMock


class ScanPointGeneratorBaseTest(ScanPointGeneratorTest):

    def setUp(self):
        self.g = Generator()

    def test_init(self):
        self.assertEqual(self.g.position_units, None)
        self.assertEqual(self.g.index_dims, None)
        self.assertEqual(self.g.index_names, None)
        self.assertRaises(NotImplementedError, self.g.iterator)

    def test_to_dict_raises(self):
        with self.assertRaises(NotImplementedError):
            self.g.to_dict()

    def test_from_dict(self):
        m = MagicMock()
        self.g._generator_lookup['TestGenerator'] = m

        gen_dict = dict(typeid="TestGenerator")
        self.g.from_dict(gen_dict)

        m.from_dict.assert_called_once_with(gen_dict)

    def test_register_subclass(self):

        @Generator.register_subclass("TestGenerator")
        class TestGenerator(object):
            pass

        self.assertEqual(TestGenerator, Generator._generator_lookup["TestGenerator"])


if __name__ == "__main__":
    unittest.main()
