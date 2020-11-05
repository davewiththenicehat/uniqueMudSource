from evennia.commands.default.tests import CommandTest
from commands import developer_cmds
from typeclasses.characters import Character
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from evennia import create_object


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
    character_typeclass = Character
    exit_typeclass = Exit
    room_typeclass = Room
    # script_typeclass = DefaultScript

    def test_cmds(self):

        # make character names something easy to tell apart
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'

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
        wanted_message = "You will be busy for \\d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \\d+ VS punch \\d+: You attempt to evade Char2's punch "
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
        # Make a test hat
        test_hat = create_object(clothing.Clothing, key="test hat")
        test_hat.db.clothing_type = "hat"
        test_hat.location = self.char1
        # Make a test scarf
        test_scarf = create_object(clothing.Clothing, key="test scarf")
        test_scarf.db.clothing_type = "accessory"
        test_scarf.location = self.char1
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
        # Test wearing an item that is not clothing
        command = developer_cmds.CmdMultiCmd
        arg = "= wear Obj"
        wanted_message = "You can only wear clothing and armor."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)


# test commands that have code desicated to clothing module
from typeclasses.equipment import clothing
from commands.standard_cmds import CmdDrop, CmdInventory

"""

        self.call(
            clothing.CmdWear(),
            "scarf stylishly",
            "Wearer wears test scarf stylishly.",
            caller=wearer,
        )
        # Test cover command.
        self.call(
            clothing.CmdCover(),
            "",
            "Usage: cover <worn clothing> [with] <clothing object>",
            caller=wearer,
        )

        self.call(
            clothing.CmdCover(),
            "hat with scarf",
            "Wearer covers test hat with test scarf.",
            caller=wearer,
        )
        # Test remove command.
        self.call(clothing.CmdRemove(), "", "Could not find ''.", caller=wearer)
        self.call(
            clothing.CmdRemove(), "hat", "You have to take off test scarf first.", caller=wearer
        )
        self.call(
            clothing.CmdRemove(),
            "scarf",
            "Wearer removes test scarf, revealing test hat.",
            caller=wearer,
        )
        # Test uncover command.
        test_scarf.wear(wearer, True)
        test_hat.db.covered_by = test_scarf
        self.call(clothing.CmdUncover(), "", "Usage: uncover <worn clothing object>", caller=wearer)
        self.call(clothing.CmdUncover(), "hat", "Wearer uncovers test hat.", caller=wearer)
        # Test drop command.
        test_hat.db.covered_by = test_scarf
        self.call(CmdDrop(), "", "Drop what?", caller=wearer)
        self.call(
            CmdDrop(),
            "hat",
            "You can't drop that because it's covered by test scarf.",
            caller=wearer,
        )
        self.call(CmdDrop(), "scarf", "You drop test scarf.", caller=wearer)
        # Test inventory command.
        command = CmdInventory
        arg = ""
        wanted_message = "You are carrying:\n Nothing\\.   \r\nYou are wearing:\n test hat"
        cmd_result = self.call(command(), arg, caller=wearer)
        self.assertRegex(cmd_result, wanted_message)
        #empty inventory
        command = CmdDrop
        arg = "hat"
        wanted_message = "You drop test hat."
        cmd_result = self.call(command(), arg, wanted_message, caller=wearer)
        #test empty inventory
        command = CmdInventory
        arg = ""
        wanted_message = "You are not carrying or wearing anything."
        cmd_result = self.call(command(), arg, wanted_message, caller=wearer)
        # attempt to wear an item not in inventory
        command = clothing.CmdWear
        arg = "hat"
        wanted_message = "You do not have hat to wear.\nTry picking it up first with get hat."
        cmd_result = self.call(command(), arg, caller=wearer)
        self.assertRegex(cmd_result, wanted_message)
"""
