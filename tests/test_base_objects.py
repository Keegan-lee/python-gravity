import unittest
from gravity import Gravity, exceptions
from gravity.instance import set_shared_gravity_instance
from gravity.account import Account
from gravity.committee import Committee


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grv = Gravity(
            nobroadcast=True,
        )
        set_shared_gravity_instance(self.grv)

    def test_Committee(self):
        with self.assertRaises(
            exceptions.AccountDoesNotExistsException
        ):
            Committee("FOObarNonExisting")

        c = Committee("init0")
        self.assertEqual(c["id"], "1.5.0")
        self.assertIsInstance(c.account, Account)

        with self.assertRaises(
            exceptions.CommitteeMemberDoesNotExistsException
        ):
            Committee("nathan")
