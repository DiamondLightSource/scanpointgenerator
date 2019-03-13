import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from scanpointgenerator import Mutator

from pkg_resources import require
require("mock")
from mock import MagicMock


class MutatorTest(unittest.TestCase):

    def test_mutate_raises(self):
        m = Mutator()
        with self.assertRaises(NotImplementedError):
            m.mutate(MagicMock(), MagicMock())


class SerialisationTest(unittest.TestCase):

    def setUp(self):
        self.m = Mutator()

    def test_to_dict(self):
        expected = {}
        self.assertEqual(expected, self.m.to_dict())

if __name__ == "__main__":
    unittest.main()
