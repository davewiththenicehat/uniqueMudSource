from evennia.utils.test_resources import EvenniaTest
from evennia.commands.default.tests import CommandTest
from evennia import create_object

from typeclasses.accounts import Account
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from typeclasses.scripts import Script
from typeclasses.equipment.wieldable import OneHandedWeapon


class UniqueMudTest(EvenniaTest):
    """
    Base test for UniqueMud, sets up a basic environment.

    Objects in EvenniaTest
        self.obj1 = "Obj"
        self.obj2 = "Obj2"
        self.char1 = "Char"
            self.char1.account = self.account
            self.char1.permissions.add("Developer")
            self.account.permissions.add("Developer")
        self.char2 = "Char2"
            self.char2.account = self.account2
        self.exit = "out"
        self.room1 = "Room"
    """

    account_typeclass = Account
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    script_typeclass = Script

    def setUp(self):
        """
        Sets up testing environment
        """
        # call inherited setUp
        super().setUp()
        # make character names something easy to tell apart,
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'
        # make objects targetable for testing
        self.obj1.targetable = True
        self.obj2.targetable = True
        self.sword = create_object(OneHandedWeapon, key="a sword")
        self.sword.targetable = True
        self.sword.location = self.char1.location


class UniqueMudCmdTest(UniqueMudTest, CommandTest):
    pass
