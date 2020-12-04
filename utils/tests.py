from evennia.commands.default.tests import CommandTest
from evennia import create_object
from typeclasses.characters import Character
from evennia.contrib import gendersub
from utils.element import Element
from utils import um_utils


class TestUtils(CommandTest):
    """
    Used to test the utilities

    Objects in EvenniaTest
        self.obj1 self.obj2 self.char1 self.char2 self.exit
    """
    def test_utils(self):

        # test setting Element
        char = create_object(Character, key="Gendered", location=self.room1)
        self.assertEqual(char.hp, 100)
        self.assertNotEqual(char.hp, 99)
        self.assertIsInstance(char.hp, Element)
        char.hp = 10
        self.assertIsInstance(char.hp, Element)
        self.assertEqual(char.hp, 10)

        # test math operators
        self.assertEqual(char.hp + 10, 20)
        self.assertEqual(10 + char.hp, 20)
        char.hp += 10
        self.assertEqual(char.hp, 20)

        char.hp = 10
        self.assertEqual(char.hp - 5, 5)
        self.assertEqual(5 - char.hp, 5)
        char.hp -= 5
        self.assertEqual(char.hp, 5)

        char.hp = 10
        self.assertEqual(char.hp * 2, 20)
        self.assertEqual(2 * char.hp, 20)
        char.hp *= 2
        self.assertEqual(char.hp, 20)

        char.hp = 10
        self.assertEqual(char.hp / 2, 5)
        self.assertEqual(2 / char.hp, 5)
        char.hp /= 2
        self.assertEqual(char.hp, 5)

        char.hp = 10
        self.assertEqual(char.hp ** 2, 100)
        self.assertEqual(2 ** char.hp, 100)
        # char.hp **= 2
        # self.assertEqual(char.hp, 100)

        char.hp = 11
        self.assertEqual(char.hp // 2, 5)
        self.assertEqual(2 // char.hp, 5)
        char.hp //= 2
        self.assertEqual(char.hp, 5)

        char.hp = 11
        self.assertEqual(char.hp % 2, 1)
        self.assertEqual(2 % char.hp, 1)
        char.hp %= 2
        self.assertEqual(char.hp, 1)

        # make certain element can save as full float
        char.hp = 11
        char.hp = ((char.hp / 2) / 2) / 2
        self.assertEqual(char.hp, 1.375)

        # test percentage functions
        char.hp = 33
        self.assertEqual(char.hp.percentage(), 33)
        self.assertEqual(char.hp.breakpoint_percent(), 33)
        char.hp.breakpoint = 10
        self.assertEqual(char.hp.breakpoint_percent(), 25.56)
        char.hp.breakpoint = 0

        # test standard operators
        self.assertTrue(char.hp < 34)
        self.assertFalse(char.hp < 33)
        self.assertTrue(char.hp <= 34)
        self.assertTrue(char.hp > 32)
        self.assertFalse(char.hp > 33)
        self.assertTrue(char.hp >= 32)
        self.assertTrue(char.hp == 33)
        self.assertTrue(char.hp != 34)

        # test setting attributes
        char.hp = 100
        self.assertEqual(char.attributes.get('hp_value'), 100)
        char.hp = 33
        self.assertEqual(char.attributes.get('hp_value'), 33)

        self.assertEqual(char.attributes.get('hp_breakpoint'), 0)
        char.hp.breakpoint = 10
        self.assertEqual(char.attributes.get('hp_breakpoint'), 10)
        char.hp.breakpoint = 0
        self.assertEqual(char.attributes.get('hp_breakpoint'), 0)

        self.assertFalse(char.attributes.has('hp_min'))
        char.hp.min = -99
        self.assertEqual(char.attributes.get('hp_min'), -99)
        char.hp.min = -100
        self.assertEqual(char.attributes.get('hp_min'), -100)

        self.assertFalse(char.attributes.has('hp_max'))
        char.hp.max = 101
        self.assertEqual(char.attributes.get('hp_max'), 101)
        char.hp.max = 100
        self.assertEqual(char.attributes.get('hp_max'), 100)

        # test element functions
        def br_func():
            char.descending_breakpoint_reached = True
        def as_br_func():
            char.ascending_breakpoint_reached = True
        char.hp.descending_breakpoint_func = br_func
        char.hp.ascending_breakpoint_func = as_br_func
        char.hp = -1
        self.assertTrue(char.descending_breakpoint_reached)
        # reset it and do it again
        char.descending_breakpoint_reached = False
        char.hp = 1
        self.assertTrue(char.ascending_breakpoint_reached)  # test ascending breakpoints
        self.assertFalse(char.descending_breakpoint_reached)  # test descending breakpoints a second time.
        char.hp = -1
        self.assertTrue(char.descending_breakpoint_reached)
        # clean up temp variables
        char.ascending_breakpoint_reached = None
        char.descending_breakpoint_reached = None


        def min_test_func():
            char.min_reached = True
        char.hp.min_func = min_test_func
        char.hp -= 400
        self.assertTrue(char.min_reached)

        def max_test_func():
            char.max_reached = True
        char.hp.max_func = max_test_func
        char.hp += 200
        self.assertTrue(char.max_reached)

        # make certain the Element is still an element, not an int
        self.assertIsInstance(char.hp, Element)

        # test element deletion
        del char.hp
        self.assertFalse(char.attributes.has('hp_value'))

        # test um_utils.highlighter
        # test highlighting
        test_message = um_utils.highlighter('test', 'r')
        self.assertEqual(test_message, "|[rtest|n")
        # test a text color change
        test_message = um_utils.highlighter('test', color='r')
        self.assertEqual(test_message, "|rtest|n")
        # test click kwarg
        test_message = um_utils.highlighter('test', click=True)
        self.assertEqual(test_message, "|lctest|lttest|le|n")
        # test a custom click command
        test_message = um_utils.highlighter('test', click_cmd="click me")
        self.assertEqual(test_message, "|lcclick me|lttest|le|n")
        # test the up kwarg
        test_message = um_utils.highlighter('test', up=True)
        self.assertEqual(test_message, "Test|n")

        # test error reporting utility
        report_msg = um_utils.error_report("test error")
        self.assertEqual(report_msg, "test error")
        report_msg = um_utils.error_report("test error", char)
        self.assertRegex(report_msg, r"^An error was found and has been logged")
        report_msg = um_utils.error_report("test error", self.char1)
        self.assertRegex(report_msg, r"System detects you are a developer\.$")
