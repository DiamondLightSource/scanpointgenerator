import unittest

from scanpointgenerator.mutator import Mutator

from pkg_resources import require
require("mock")
from mock import MagicMock


class MutatorTest(unittest.TestCase):

    def setUp(self):
        self.m = Mutator()

    def test_init(self):
        self.assertEqual({}, self.m._mutator_lookup)

    def test_mutate_raises(self):
        with self.assertRaises(NotImplementedError):
            self.m.mutate(MagicMock())

    def test_register_subclass(self):

        @Mutator.register_subclass("TestMutator")
        class TestMutator(object):
            pass

        self.assertEqual(TestMutator, Mutator._mutator_lookup["TestMutator"])


class SerialisationTest(unittest.TestCase):

    def setUp(self):
        self.m = Mutator()

    def test_to_dict_raises(self):
        with self.assertRaises(NotImplementedError):
            self.m.to_dict()

    def test_from_dict(self):
        m = MagicMock()
        self.m._mutator_lookup['TestMutator'] = m

        gen_dict = dict(type="TestMutator")
        self.m.from_dict(gen_dict)

        m.from_dict.assert_called_once_with(gen_dict)
