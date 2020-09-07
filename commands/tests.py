import unittest
from evennia.commands.default.tests import CommandTest
from commands.command import CmdAbilities
from typeclasses.characters import Character
from typeclasses.objects import Object
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from evennia.utils.test_resources import EvenniaTest
from evennia.commands.default import general
from commands.magicfire import CmdBlaze
"""
Created following: https://github.com/evennia/evennia/wiki/Unit-Testing#testing-for-game-development-mini-tutorial
"""

class TestString(unittest.TestCase):

    """Unittest for strings (just a basic example)."""

    def test_upper(self):
        """Test the upper() str method."""
        self.assertEqual('foo'.upper(), 'FOO')

class TestAbilities(CommandTest):

    character_typeclass = Character

    def test_simple(self):
        cmd_abil_result = self.call(CmdAbilities(), "")
        expected_regex_pattern = "level \d+, HP \d+, XP \d+, STR \d+, combat \d+"
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRegex
        self.assertRegex(cmd_abil_result, "level \d+, HP \d+, XP \d+, STR \d+, combat \d+")


class TestObject(EvenniaTest):

    # change default variables to our classes
    character_typeclass = Character
    object_typeclass = Object
    exit_typeclass = Exit
    room_typeclass = Room

    def test_object_search(self):
        # char1 and char2 are both created in room1
        self.assertEqual(self.char1.search(self.char2.key), self.char2)
        self.assertEqual(self.char1.search(self.char1.location.key), self.char1.location)


class TestSet(CommandTest):

    # change default variables to our classes
    character_typeclass = Character
    object_typeclass = Object
    exit_typeclass = Exit
    room_typeclass = Room

    "tests the look command by simple call, using Char2 as a target"
    def test_mycmd_char(self):
        self.call(general.CmdLook(), "Char2", "Char2(#7)")

    def test_object_invisibility(self):
        self.obj2.make_invisible()
        self.call(general.CmdLook(), "Obj2", "Could not view 'Obj2'.", caller=self.char2)
        self.obj2.make_visible()

    def test_magic_fire_cmd_set(self):
         self.call(CmdBlaze(), "", "Char summons blazing fire that lights the room.")

    def test_stunned(self):
        from commands.stunned import CmdBlaze
        self.call(CmdBlaze(), "", "You can not do that while stunnded.")

    def test_attack(self):
        from commands.command import CmdAttack
        attack_result = self.call(CmdAttack(), "char2")
        self.char1.ready_timer.cancel()  # stop the ready timer
        self.char1.cool_down = None  # remove the cool_down variable
        expected_regex_pattern = "^Char rolls \d+ \+ combat \d+ = \d+ | Char2 rolls \d+ \+ combat \d+ = \d+"
        self.assertRegex(attack_result, expected_regex_pattern)
        expected_regex_pattern = "Char \d+ vs Char2 \d+"
        self.assertRegex(attack_result, expected_regex_pattern)
        expected_regex_pattern = "You will be busy for 10 seconds.$"
        self.assertRegex(attack_result, expected_regex_pattern)
