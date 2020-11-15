from evennia.commands.default.tests import CommandTest
from commands import developer_cmds
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from evennia import create_object
from typeclasses.equipment import clothing


class TestCommands(CommandTest):

    """
        CommandTest.call arguments
        call(cmdobj, args, msg=None, cmdset=None,
            noansi=True, caller=None, receiver=None, cmdstring=None,
            obj=None, inputs=None, raw_string=None,
        ):
    Objects in EvenniaTest
        self.obj1 self.obj2 self.char1 self.char2 self.exit
    """
    # account_typeclass = DefaultAccount
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    # script_typeclass = DefaultScript

    def test_cmds(self):

        # make character names something easy to tell apart
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'

    # misc command test
        # provide a target that does not exist with a command requiring a target
        #command = developer_cmds.CmdMultiCmd
        #arg = "= wear none existant object"
        #wanted_message = "none existant object is not here."
        #self.call(command(), arg, wanted_message)

    # test deffering commands
        # defer a command and complete it
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, complete_cmd_early"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
        self.call(command(), arg, wanted_message)

        # request a deffered command to stop
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # you can not fullow up a busy command with another busy command
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, defer_cmd"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|You will be busy for 5 seconds."
        self.call(command(), arg, wanted_message)

        # force a deffered command to stop, a deffered command was left open on 'char' from the test above
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd"
        wanted_message = "You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on self when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd"
        wanted_message = "You may want to test_cmd.|You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # complete a command early when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wanted_message = "You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on a target that has no deffered command
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd Char2, l"
        wanted_message = "Char2 is not commited to an action."
        self.call(command(), arg, wanted_message)

        # request target to stop a deffered comamnd
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun a character and stop it early
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, stop_stun"
        wanted_message = "You will be stunned for 3 seconds.|You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun locks out busy commands
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, defer_cmd"
        wanted_message = "You will be stunned for 3 seconds.|You will be stunned for 3 seconds."
        self.call(command(), arg, wanted_message)

        # stop a stun on self when there is no stun
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_stun"
        wanted_message = "You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)  # stop the stun above
        wanted_message = "You are not currently stunned."
        self.call(command(), arg, wanted_message)

    # test punch, kick and dodge
        # test punch
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Char2.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test kick
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade \\d+: You kick at Char2'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test dodge
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, control_other Char2=punch Char, complete_cmd_early Char2"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \d+ VS punch \d+: Char2 punches at you with their fist "
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test attacking an Object
        self.obj1.targetable = True
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Obj, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Obj Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Obj'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test a target leaving melee range
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, control_other Char2=out, complete_cmd_early"
        wanted_message = "You can no longer reach Char2\\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # get Char2 back into the room.
        self.char2.location = self.room1
        self.assertEqual(self.char2.location, self.room1)

        # test commands that can not target self
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char"
        wanted_message = 'You can not punch yourself.'
        cmd_result = self.call(command(), arg, wanted_message)

        # test attaking an exit that is not targetable
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out"
        wanted_message = 'You can not punch out.'
        cmd_result = self.call(command(), arg, wanted_message)

        # test attaking a targetable exit
        self.exit.targetable = True
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out, complete_cmd_early"
        wanted_message = "You will be busy for \\d+ seconds.\nFacing out Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade 5: You punch at out"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        self.exit.targetable = False

        # test a targeted command that has a stop_request against an object
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Obj, complete_cmd_early"
        wanted_message = "You will be busy for \\d+ seconds.\nFacing Obj Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade 5: You kick at Obj"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

    # test clothing commands
        # test character with empty inventory
        command = developer_cmds.CmdMultiCmd
        arg = "= inv"
        wanted_message = "You are not carrying or wearing anything."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Make a test hat
        test_hat = create_object(clothing.Clothing, key="test hat")
        test_hat.db.clothing_type = "hat"
        test_hat.location = self.char1
        # Make a test shirt
        test_shirt = create_object(clothing.Clothing, key="test shirt")
        test_shirt.db.clothing_type = "top"
        test_shirt.location = self.char1
        # Make a test helmet
        test_helmet = create_object(clothing.HumanoidArmor, key="test helmet")
        test_helmet.db.clothing_type = "head"
        test_helmet.at_init()  # TestCommands will not call at_init hooks.
        test_helmet.location = self.char1
        # give the helmet an armor rating
        test_helmet.dr.PRC = 2
        test_helmet.dr.ACD = 3
        self.assertEqual(test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(test_helmet.dr.PRC, 2)
        # Test wear with no arguments.
        command = clothing.CmdWear
        arg = ""
        wanted_message = "What would you like to wear?|If you need help try help wear."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test tring to wear an item not on person also tests Command.search_caller_only
        command = developer_cmds.CmdMultiCmd
        arg = "= wear Obj"
        wanted_message = "Try picking it up first with get Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test tring to wear an item that is not clothing, also tests target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj"
        wanted_message = "You pick up Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= wear Obj"
        wanted_message = "You can only wear clothing and armor."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= drop Obj"
        wanted_message = "You drop Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test removing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= remove hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar removes test hat.\nYou are no longer busy.\nChar allowed you to complete your remove command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Put the hat back on to test covering
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing a peace of armor
        command = developer_cmds.CmdMultiCmd
        arg = "= wear helmet, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test helmet.\nChar puts on test helmet, covering test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test character with items worn and not
        command = developer_cmds.CmdMultiCmd
        arg = "= inv"
        wanted_message = "You are carrying:\n test shirt   \r\nYou are wearing:\n test hat      \n test helmet"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        #misc tests
        self.assertEqual(test_hat.db.worn, True)
        self.assertEqual(test_hat.db.clothing_type, 'hat')
        self.assertEqual(test_helmet.db.clothing_type, "head")
        self.assertTrue('head' in test_helmet.type_limit)
        # Make certain return_appearance is working
        self.assertEqual(self.char1.return_appearance(self.char1), "You are wearing test helmet.")
        # Test now with the look command
        command = developer_cmds.CmdMultiCmd
        arg = "= l me"
        wanted_message = "You are wearing test helmet."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test clothing covering.
        # Make a test shirt
        test_undershirt = create_object(clothing.Clothing, key="test undershirt")
        test_undershirt.db.clothing_type = "undershirt"
        test_undershirt.location = self.char1
        # Test wearing the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear undershirt, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test undershirt.\nChar puts on test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing the shirt covering the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test shirt.\nChar puts on test shirt, covering test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        self.assertEqual(test_undershirt.db.covered_by, test_shirt)
        #verify that the helmet's armor rating has been cached in the wearer
        self.assertEqual(self.char1.body.head.dr.PRC, 2)
        self.assertEqual(self.char1.body.head.dr.ACD, 3)
        self.assertEqual(self.char1.body.head.dr.BLG, 0)

        # test function get_body_part
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, char2"
        wanted_message = r"get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertFalse(cmd_result == wanted_message)
        # now test an object with no body parts
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, obj"
        wanted_message = r"^get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test function damage after damage reduction
        command = developer_cmds.CmdCmdFuncTest
        command.dmg_types = ["ACD", "PRC"]  # give two types whose armor has different values
        arg = "/r dmg_after_dr, char = 3, head"
        wanted_message = "dmg_after_dr returned: 1"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # make certain the lowest number returned is 0
        command = developer_cmds.CmdCmdFuncTest
        command.dmg_types = ["ACD", "PRC"]  # give two types whose armor has different values
        arg = "/r dmg_after_dr, char = 0, head"
        wanted_message = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # now change the targets dr to make certain that affects
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        command.dmg_types = ["ACD", "PRC"]  # give two types whose armor has different values
        arg = "/r dmg_after_dr, char = 3, head"
        wanted_message = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # Verify giving None as dmg_dealt works
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        command.dmg_types = ["ACD", "PRC"]  # give two types whose armor has different values
        arg = "/r dmg_after_dr, char = None, head"
        wanted_message = r"dmg_after_dr returned: \d+"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
