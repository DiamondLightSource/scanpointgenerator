import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from test_util import ScanPointGeneratorTest
from scanpointgenerator import Excluder

from pkg_resources import require
require("mock")
from mock import MagicMock


class ExcluderTest(unittest.TestCase):

    def test_init(self):
        Excluder(["x", "y"])


class SimpleFunctionsTest(unittest.TestCase):

    def setUp(self):
        self.e = Excluder(["x", "y"])

    def test_create_mask(self):
        with self.assertRaises(NotImplementedError):
            self.e.create_mask(MagicMock(), MagicMock())


class SerialisationTest(unittest.TestCase):

    def setUp(self):
        self.e = Excluder(["x", "y"])

    def test_to_dict(self):
        expected_dict = dict()
        expected_dict['axes'] = ["x", "y"]

        d = self.e.to_dict()

        self.assertEqual(expected_dict, d)

    def test_from_dict(self):
        m = MagicMock()
        self.e._excluder_lookup['TestMutator'] = m

        gen_dict = dict(typeid="TestMutator")
        self.e.from_dict(gen_dict)

        m.from_dict.assert_called_once_with(gen_dict)

if __name__ == "__main__":
    unittest.main()
