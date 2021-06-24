from unittest import mock

from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import TestCase
from evennia import create_object

from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from commands import developer_cmds
from world.rules import body
from utils.element import Element
from utils import um_utils
from utils.unit_test_resources import UniqueMudCmdTest
from world.rules.stats import STATS
from world.rules import skills


class TestRules(CommandTest):

    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room

    def test_rules(self):
        """
        Used to test the character object
        stat modifiers unit tests are in world.rules.tests.TestRules.test_stat_modifiers

        CommandTest.call arguments
        call(cmdobj, args, msg=None, cmdset=None,
            noansi=True, caller=None, receiver=None, cmdstring=None,
            obj=None, inputs=None, raw_string=None,
        ):

        Objects in EvenniaTest
            self.obj1 = obj
            self.obj2 = "obj2"
            self.char1 = "char"
            self.char2 = "char2"
            self.exit = "out"
        """
        #initialize stat modifier cache
        self.char1.at_init()
        self.char2.at_init()
        # make character names something easy to tell apart
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'
        # make objects targetable for testing
        self.obj1.targetable = True
        self.obj2.targetable = True
        self.obj3 = create_object(Object, key="Obj3")
        self.obj3.targetable = True
        self.obj3.location = self.char1.location
        # check that stats mods are at correct value for stats all being max 100
        command = developer_cmds.CmdViewObj
        arg = " =stat_cache"
        wanted_message = "Character ID: 6 STR_evade_mod: 33|Character ID: 6 STR_action_mod: 20|Character ID: 6 STR_action_cost_mod: 0.25|Character ID: 6 STR_dmg_mod: 4|Character ID: 6 STR_restoration_mod: 2|Character ID: 6 CON_evade_mod: 33|Character ID: 6 CON_action_mod: 20|Character ID: 6 CON_action_cost_mod: 0.25|Character ID: 6 CON_dmg_mod: 4|Character ID: 6 CON_restoration_mod: 2|Character ID: 6 OBS_evade_mod: 33|Character ID: 6 OBS_action_mod: 20|Character ID: 6 OBS_action_cost_mod: 0.25|Character ID: 6 OBS_dmg_mod: 4|Character ID: 6 OBS_restoration_mod: 2|Character ID: 6 AGI_evade_mod: 33|Character ID: 6 AGI_action_mod: 20|Character ID: 6 AGI_action_cost_mod: 0.25|Character ID: 6 AGI_dmg_mod: 4|Character ID: 6 AGI_restoration_mod: 2|Character ID: 6 SPD_evade_mod: 33|Character ID: 6 SPD_action_mod: 20|Character ID: 6 SPD_action_cost_mod: 0.25|Character ID: 6 SPD_dmg_mod: 4|Character ID: 6 SPD_restoration_mod: 2|Character ID: 6 INT_evade_mod: 33|Character ID: 6 INT_action_mod: 20|Character ID: 6 INT_action_cost_mod: 0.25|Character ID: 6 INT_dmg_mod: 4|Character ID: 6 INT_restoration_mod: 2|Character ID: 6 WIS_evade_mod: 33|Character ID: 6 WIS_action_mod: 20|Character ID: 6 WIS_action_cost_mod: 0.25|Character ID: 6 WIS_dmg_mod: 4|Character ID: 6 WIS_restoration_mod: 2|Character ID: 6 CHR_evade_mod: 33|Character ID: 6 CHR_action_mod: 20|Character ID: 6 CHR_action_cost_mod: 0.25|Character ID: 6 CHR_dmg_mod: 4|Character ID: 6 CHR_restoration_mod: 2|Character ID: 6 hp_max_mod: 33|Character ID: 6 endurance_max_mod: 33|Character ID: 6 sanity_max_mod: 33|Character ID: 6 load_max_mod: 100|Character ID: 6 busy_mod: 0.25|Character ID: 6 stunned_mod: 0.25|Character ID: 6 purchase_mod: 0.25"
        self.call(command(), arg, wanted_message)

        # test body.get_part
        body_part = body.get_part(self.char1)
        self.assertTrue(body_part.name in self.char1.body.parts)
        # make certain getting a specific part works.
        body_part = body.get_part(self.char1, 'head')
        part_name = body_part.name
        part_name_direct = self.char1.body.head.name
        self.assertTrue(part_name == part_name_direct)
        # make certain it returns false on fail
        fail_body_part = body.get_part(self.char1, 'no_part_name')
        self.assertFalse(fail_body_part)

        # test dodge
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 52"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # Test Character ranks in an evade skill, action or command
        self.char1.skills.evasion.dodge = 1
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 52"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        self.char1.skills.evasion.dodge = 10
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 59"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        self.char1.skills.evasion.dodge = 20
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 67"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test Character ranks in a standard skill, action or command
        # defer a punch to use within rules.actions.action_roll
        command = developer_cmds.CmdMultiCmd
        arg = "= punch char2"
        wanted_message = 'You will be busy for 3 seconds.|Facing char2(#7) you pull your hand back preparing an attack.'
        cmd_result = self.call(command(), arg, wanted_message)
        # test 1 skill rank
        self.char1.skills.unarmed.punch = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "action_roll, self, cmd_type:unarmed, evade_mod_stat:OBS, skill_name:punch = False, True"
        wanted_message = r"roll_max: 51"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # test 10 skill ranks
        self.char1.skills.unarmed.punch = 10
        command = developer_cmds.CmdCmdFuncTest
        arg = "action_roll, self, cmd_type:unarmed, evade_mod_stat:OBS, skill_name:punch = False, True"
        wanted_message = r"roll_max: 58"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # test 20 skill ranks
        self.char1.skills.unarmed.punch = 20
        command = developer_cmds.CmdCmdFuncTest
        arg = "action_roll, self, cmd_type:unarmed, evade_mod_stat:OBS, skill_name:punch = False, True"
        wanted_message = r"roll_max: 66"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # Complete the deffered punch
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wanted_message = 'punch \\d+ VS evade \\d+: You punch at char2\(#7\)\.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        self.char1.skills.unarmed.punch = 0

class TestSkills(CommandTest):

    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room

    def test_rank_requirement(self):
        self.assertEqual(skills.rank_requirement(1, 'very easy'), 300)
        self.assertEqual(skills.rank_requirement(3, 'very easy'), 900)
        self.assertEqual(skills.rank_requirement(1, 'easy'), 375)
        self.assertEqual(skills.rank_requirement(3, 'easy'), 1125)
        self.assertEqual(skills.rank_requirement(1, 'moderate'), 450)
        self.assertEqual(skills.rank_requirement(3, 'moderate'), 1350)
        self.assertEqual(skills.rank_requirement(1, 'hard'), 525)
        self.assertEqual(skills.rank_requirement(3, 'hard'), 1575)
        self.assertEqual(skills.rank_requirement(1, 'daunting'), 600)
        self.assertEqual(skills.rank_requirement(3, 'daunting'), 1800)
        for learn_diff in skills. DIFFICULTY_LEVELS.values():
            self.assertEqual(len(skills._RANK_REQUIREMENTS[learn_diff]), 4)


class TestUtils(UniqueMudCmdTest):
    """
    Used to test the utilities

    Objects in EvenniaTest
        self.obj1 self.obj2 self.char1 self.char2 self.exit
    """

    def cap_msg(self):
        for punc in '.?!':
            sentence = um_utils.cap_msg(f'this is a Dave sentence{punc} sec{punc}ond sentence{punc}')
            exp_sentence = f'This is a Dave sentence{punc} Sec{punc}ond sentence{punc}'
            self.assertEqual(sentence, exp_sentence)

    def test_element(self):
        """
        test utils.element.Element
        """
        char = self.char1

        # test setting Element
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
        self.assertEqual(5 - char.hp, -5)
        char.hp -= 5
        self.assertEqual(char.hp, 5)

        char.hp = 10
        self.assertEqual(char.hp * 2, 20)
        self.assertEqual(2 * char.hp, 20)
        char.hp *= 2
        self.assertEqual(char.hp, 20)

        char.hp = 10
        self.assertEqual(char.hp / 2, 5)
        self.assertEqual(2 / char.hp, 0.2)
        char.hp /= 2
        self.assertEqual(char.hp, 5)

        char.hp = 10
        self.assertEqual(char.hp ** 2, 100)
        self.assertEqual(2 ** char.hp, 1024.0)
        char.hp = 3
        char.hp **= 2
        self.assertEqual(char.hp, 9)

        char.hp = 11
        self.assertEqual(char.hp // 2, 5)
        char.hp = 2
        self.assertEqual(11 // char.hp, 5)
        char.hp = 11
        char.hp //= 2
        self.assertEqual(char.hp, 5)

        char.hp = 11
        self.assertEqual(char.hp % 2, 1)
        char.hp = 12
        self.assertEqual(5 % char.hp, 5)
        char.hp = 17
        char.hp %= 12
        self.assertEqual(char.hp, 5)

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

        # self.assertEqual(char.hp, 100)

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
        # verify attr is still an Element
        self.assertIsInstance(char.hp, Element)

        # run tests on an instance of a Element object
        for stat in ("endurance", "strength"):

            # get stat instance
            st_ins = getattr(self.char1, stat, False)
            if not st_ins:
                err_msg = "world.rules.tests.TestUtils.test_element, failed " \
                          f"to find self.char1.{stat}"
                raise AssertionError(err_msg)

            # test setting Element
            self.assertEqual(st_ins, 100)
            self.assertNotEqual(st_ins, 99)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # set the instance
            st_ins.set(10)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 10)
            self.assertEqual(st_ins, 10)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test add descriptors
            st_ins.set(50)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 50)
            # test __radd__
            self.assertEqual(st_ins + 10, 60)
            # test __add__
            self.assertEqual(10 + st_ins, 60)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test sub descriptors
            st_ins.set(50)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 50)
            # test __rsub__
            self.assertEqual(st_ins - 10, 40)
            # test __sub__
            self.assertEqual(10 - st_ins, -40)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test mul descriptors
            st_ins.set(4)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 4)
            # test __rmul__
            self.assertEqual(st_ins * 10, 40)
            # test __mul__
            self.assertEqual(10 * st_ins, 40)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test truediv descriptors
            st_ins.set(2)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 2)
            # test __truediv__
            self.assertEqual(st_ins / 3, 0.6666666666666666)
            # test __rtruediv__
            self.assertEqual(3 / st_ins, 1.5)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test floordiv descriptors
            st_ins.set(11)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 11)
            # test __floordiv__
            self.assertEqual(st_ins // 2, 5)
            # test __rfloordiv__
            st_ins.set(2)
            self.assertEqual(11 // st_ins, 5)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test modulo division descriptors
            st_ins.set(11)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 11)
            # test __mod__
            self.assertEqual(st_ins % 2, 1)
            # test __rmod__
            st_ins.set(2)
            self.assertEqual(11 % st_ins, 1)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test power descriptors
            st_ins.set(2)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 2)
            # test __pow__
            self.assertEqual(st_ins ** 3, 8)
            # test __rpow__
            st_ins.set(3)
            self.assertEqual(st_ins ** 2, 9)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test standard operators
            st_ins.set(33)
            # verify change in database was recorded.
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 33)
            self.assertTrue(st_ins < 34)
            self.assertFalse(st_ins < 33)
            self.assertTrue(st_ins <= 34)
            self.assertTrue(st_ins > 32)
            self.assertFalse(st_ins > 33)
            self.assertTrue(st_ins >= 32)
            self.assertTrue(st_ins == 33)
            self.assertTrue(st_ins != 34)

            # test setting attributes
            st_ins.set(100)
            st_ins.set(33)
            self.assertEqual(char.attributes.get(f'{st_ins.name}_value'), 33)
            # test breakpoint
            self.assertEqual(char.attributes.get(f'{st_ins.name}_breakpoint'), None)
            st_ins.breakpoint = 10
            self.assertEqual(char.attributes.get(f'{st_ins.name}_breakpoint'), 10)
            st_ins.breakpoint = 0
            self.assertEqual(char.attributes.get(f'{st_ins.name}_breakpoint'), 0)
            # test min
            self.assertFalse(char.attributes.has(f'{st_ins.name}_min'))
            st_ins.min = -99
            self.assertEqual(char.attributes.get(f'{st_ins.name}_min'), -99)
            st_ins.min = -100
            self.assertEqual(char.attributes.get(f'{st_ins.name}_min'), -100)
            # test max
            self.assertFalse(char.attributes.has(f'{st_ins.name}_max'))
            st_ins.max = 101
            self.assertEqual(char.attributes.get(f'{st_ins.name}_max'), 101)
            st_ins.max = 100
            self.assertEqual(char.attributes.get(f'{st_ins.name}_max'), 100)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test element functions
            st_ins.descending_breakpoint_func = br_func
            st_ins.ascending_breakpoint_func = as_br_func
            st_ins.set(-1)
            self.assertTrue(char.descending_breakpoint_reached)
            # reset it and do it again
            char.descending_breakpoint_reached = False
            st_ins.set(1)
            self.assertTrue(char.ascending_breakpoint_reached)  # test ascending breakpoints
            self.assertFalse(char.descending_breakpoint_reached)  # test descending breakpoints a second time.
            st_ins.set(-1)
            self.assertTrue(char.descending_breakpoint_reached)
            # clean up temp variables
            char.ascending_breakpoint_reached = None
            char.descending_breakpoint_reached = None
            # test min_func
            st_ins.max_func = max_test_func
            st_ins.set(st_ins.get() + 200)
            self.assertTrue(char.max_reached)
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            # test delet
            st_ins.delete()
            self.assertFalse(char.attributes.has(f'{st_ins.name}_value'))
            # verify attr is still an Element
            self.assertIsInstance(st_ins, Element)

            tmp = st_ins
            st_ins = 3
            st_ins = tmp

    def test_listelement(self):
        char = self.char1
        command = developer_cmds.CmdMultiCmd
        self.call(command(), "= get sword, complete_cmd_early, wield sword, get Obj, complete_cmd_early,")
        # test iterators
        for part_name in char.body.parts:
            part_inst = getattr(char.body, part_name, False)
            # test basic teration
            for part_cond in part_inst:
                if part_cond:
                    self.assertEqual(f"{type(part_cond)}", "<class 'evennia.typeclasses.attributes.Attribute'>")
            # test items method
            for cond_desc, part_cond in part_inst.items():
                if part_cond:
                    self.assertTrue(char.attributes.has(f"{part_name}_{cond_desc}"))
                else:
                    self.assertFalse(char.attributes.has(f"{part_name}_{cond_desc}"))
            for cond_desc, part_cond in part_inst.items(return_obj=True):
                if part_cond:
                    self.assertTrue(char.attributes.has(part_cond.db_key))
                else:
                    self.assertFalse(char.attributes.has(f"{part_name}_{cond_desc}"))
        # test get method
        self.assertTrue(char.body.right_hand.get('occupied'))
        self.assertFalse(char.body.right_hand.get('bleeding'))
        self.assertTrue(char.body.right_hand.get('bleeding', True))
        obj_inst = char.body.right_hand.get('occupied', return_obj=True)
        self.assertEqual(f"{type(obj_inst)}", "<class 'evennia.typeclasses.attributes.Attribute'>")
        # test contain method
        self.assertTrue('bleeding' in char.body.right_hand)
        self.assertFalse('intentional_fail' in char.body.right_hand)
        self.assertFalse(char.db.right_hand_occupied in char.body.right_hand)
        self.assertFalse(char.db.name in char.body.right_hand)
        # test __setitem__ and __getitem__ methods
        self.assertTrue(char.body.right_hand['occupied'])
        char.body.right_hand['bleeding'] = True
        self.assertTrue(char.body.right_hand['bleeding'])
        self.assertTrue(char.attributes.get('right_hand_bleeding'))
        char.body.right_hand['bleeding'] = False
        self.assertRaises(AttributeError, lambda:char.body.right_hand['int_fail'])
        self.assertRaises(TypeError, lambda:char.body.right_hand.__setitem__('int_fail'))


    def test_highlighter(self):

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

    def test_error_report(self):
        char = self.char2
        # test error reporting utility
        report_msg = um_utils.error_report("test error")
        self.assertEqual(report_msg, "test error")
        report_msg = um_utils.error_report("test error", char)
        self.assertRegex(report_msg, r"^An error was found and has been logged")
        report_msg = um_utils.error_report("test error", self.char1)
        self.assertRegex(report_msg, r"System detects you are a developer\.$")


from world.help_entries import HELP_ENTRY_DICTS
from evennia.help import filehelp

class TestFileHelp(TestCase):
    """
    Test the File-help system

    """

    @mock.patch("evennia.help.filehelp.variable_from_module")
    def test_file_help(self, mock_variable_from_module):
        mock_variable_from_module.return_value = HELP_ENTRY_DICTS

        # we just need anything here since we mock the load anyway
        storage = filehelp.FileHelpStorageHandler(help_file_modules=["dummypath"])
        result = storage.all()

        for inum, helpentry in enumerate(result):
            self.assertEqual(HELP_ENTRY_DICTS[inum]['key'].lower(), helpentry.key)
            self.assertEqual(HELP_ENTRY_DICTS[inum].get('aliases', []), helpentry.aliases)
            self.assertEqual(HELP_ENTRY_DICTS[inum]['category'], helpentry.help_category)
            self.assertEqual(HELP_ENTRY_DICTS[inum]['text'], helpentry.entrytext)
